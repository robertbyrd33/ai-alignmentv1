from flask import Flask, render_template, jsonify
import json
import os
import glob
import logging

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
# Use StreamHandler instead of RotatingFileHandler to avoid file locking issues
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info('AI Alignment Visualization startup')

# Define absolute paths correctly for Windows environment
APP_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(APP_DIR, ".."))
COMPONENTS_DIR = os.path.normpath(os.path.join(PARENT_DIR, "components"))
SUBCOMPONENTS_DIR = os.path.normpath(os.path.join(PARENT_DIR, "subcomponents"))
ROOT_JSON_FILE = os.path.normpath(os.path.join(PARENT_DIR, "ai-alignment.json"))

# Print paths to verify
app.logger.info(f"APP_DIR: {APP_DIR}")
app.logger.info(f"PARENT_DIR: {PARENT_DIR}")
app.logger.info(f"COMPONENTS_DIR: {COMPONENTS_DIR}")
app.logger.info(f"SUBCOMPONENTS_DIR: {SUBCOMPONENTS_DIR}")
app.logger.info(f"ROOT_JSON_FILE: {ROOT_JSON_FILE}")

# Default data to use if files aren't found
DEFAULT_ROOT_DATA = {
    "id": "ai-alignment",
    "name": "AI Alignment",
    "description": "Methods to ensure AI systems remain aligned with human values and intentions.",
    "type": "component_group",
    "components": [
        {
            "id": "technical-safeguards",
            "name": "Technical Safeguards",
            "description": "Engineering approaches to ensure AI systems behave as intended"
        },
        {
            "id": "value-learning",
            "name": "Value Learning",
            "description": "Systems that enable AI to learn and internalize human values"
        },
        {
            "id": "interpretability-tools",
            "name": "Interpretability Tools",
            "description": "Methods to understand AI reasoning and decision-making"
        },
        {
            "id": "oversight-mechanisms",
            "name": "Oversight Mechanisms",
            "description": "Systems for monitoring and evaluating AI behavior"
        }
    ]
}

def load_json_file(file_path):
    """Load and parse a JSON file with robust error handling."""
    try:
        app.logger.info(f"Attempting to load file: {file_path}")
        
        # Normalize path for Windows
        normalized_path = os.path.normpath(file_path)
        app.logger.info(f"Normalized path: {normalized_path}")
        
        # First check if the file exists
        if not os.path.isfile(normalized_path):
            app.logger.warning(f"File not found: {normalized_path}")
            return None
        
        # Then try to open and parse it
        with open(normalized_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            app.logger.info(f"Successfully loaded {normalized_path}")
            return data
    except json.JSONDecodeError as e:
        app.logger.error(f"JSON parsing error in {normalized_path}: {e}")
        return None
    except Exception as e:
        app.logger.error(f"Error loading {normalized_path}: {e}")
        return None

def get_root_data():
    """Get the root AI Alignment data."""
    root_data = load_json_file(ROOT_JSON_FILE)
    if not root_data:
        app.logger.warning(f"Using default root data since {ROOT_JSON_FILE} was not found")
        return DEFAULT_ROOT_DATA
    return root_data

def get_components():
    """Get all component data."""
    components = {}
    
    # Check if components directory exists
    if not os.path.isdir(COMPONENTS_DIR):
        app.logger.warning(f"Components directory not found: {COMPONENTS_DIR}")
        # Use components from the default data
        for component in DEFAULT_ROOT_DATA["components"]:
            components[component["id"]] = component
    else:
        # Load components from files
        component_files = glob.glob(os.path.join(COMPONENTS_DIR, "*.json"))
        app.logger.info(f"Found {len(component_files)} component files")
        
        for file_path in component_files:
            component_data = load_json_file(file_path)
            if component_data:
                component_id = os.path.basename(file_path).replace(".json", "")
                components[component_id] = component_data
    
    return components

def get_subcomponents():
    """Get all subcomponent data."""
    subcomponents = {}
    
    # Check if subcomponents directory exists
    if not os.path.isdir(SUBCOMPONENTS_DIR):
        app.logger.warning(f"Subcomponents directory not found: {SUBCOMPONENTS_DIR}")
        return subcomponents
    
    # Load subcomponents from files
    subcomponent_files = glob.glob(os.path.join(SUBCOMPONENTS_DIR, "*.json"))
    app.logger.info(f"Found {len(subcomponent_files)} subcomponent files")
    
    for file_path in subcomponent_files:
        data = load_json_file(file_path)
        if data:
            subcomponent_id = os.path.basename(file_path).replace(".json", "")
            if "id" not in data:
                data["id"] = subcomponent_id
            subcomponents[subcomponent_id] = data
    
    return subcomponents

def build_graph_data():
    """Build visualization graph data with nodes and links."""
    # Get data sources
    root_data = get_root_data()
    components = get_components()
    subcomponents = get_subcomponents()
    
    # Create nodes and links
    nodes = []
    links = []
    
    # Add root node
    nodes.append({
        "id": root_data["id"],
        "name": root_data["name"],
        "type": "component_group",
        "description": root_data["description"],
        "level": 0,
        "expandable": True,
        "has_children": len(components) > 0
    })
    
    # Add component nodes
    for component_id, component in components.items():
        # Check if this component has any subcomponents
        component_subcomponents = [s for s_id, s in subcomponents.items() 
                                  if "parent" in s and s["parent"] == component_id]
        has_children = len(component_subcomponents) > 0
        
        nodes.append({
            "id": component_id,
            "name": component["name"],
            "type": "component",
            "description": component.get("description", ""),
            "parent": root_data["id"],
            "level": 1,
            "expandable": has_children,
            "has_children": has_children
        })
        
        # Add link from root to component
        links.append({
            "source": root_data["id"],
            "target": component_id,
            "type": "contains"
        })
    
    # Add subcomponent nodes
    for subcomponent_id, subcomponent in subcomponents.items():
        parent_id = subcomponent.get("parent")
        if not parent_id:
            # Try to infer parent from ID
            for component_id in components:
                if component_id in subcomponent_id:
                    parent_id = component_id
                    break
        
        if parent_id:
            # Determine if subcomponent has capabilities
            capabilities = []
            if "capabilities" in subcomponent:
                if isinstance(subcomponent["capabilities"], list):
                    capabilities = subcomponent["capabilities"]
                elif isinstance(subcomponent["capabilities"], dict) and "items" in subcomponent["capabilities"]:
                    capabilities = subcomponent["capabilities"]["items"]
            
            has_children = len(capabilities) > 0
            
            nodes.append({
                "id": subcomponent_id,
                "name": subcomponent.get("name", subcomponent_id),
                "type": "subcomponent",
                "description": subcomponent.get("description", ""),
                "parent": parent_id,
                "level": 2,
                "expandable": has_children,
                "has_children": has_children
            })
            
            # Add link from component to subcomponent
            links.append({
                "source": parent_id,
                "target": subcomponent_id,
                "type": "contains"
            })
            
            # Add capability nodes
            for capability in capabilities:
                if isinstance(capability, dict) and "name" in capability:
                    capability_id = f"{subcomponent_id}-capability-{capability.get('id', capability['name'].lower().replace(' ', '-'))}"
                    
                    # Determine if capability has functions
                    functions = []
                    if "functions" in capability:
                        if isinstance(capability["functions"], list):
                            functions = capability["functions"]
                        elif isinstance(capability["functions"], dict) and "items" in capability["functions"]:
                            functions = capability["functions"]["items"]
                    
                    has_functions = len(functions) > 0
                    
                    nodes.append({
                        "id": capability_id,
                        "name": capability["name"],
                        "type": "capability",
                        "description": capability.get("description", ""),
                        "parent": subcomponent_id,
                        "level": 3,
                        "expandable": has_functions,
                        "has_children": has_functions
                    })
                    
                    # Add link from subcomponent to capability
                    links.append({
                        "source": subcomponent_id,
                        "target": capability_id,
                        "type": "has_capability"
                    })
                    
                    # Process deeper levels (functions, specifications, etc.)
                    # This is where we would add levels 4-10 as needed
                    # For brevity, implementing just through level 4 here
                    
                    # Add function nodes
                    for function in functions:
                        if isinstance(function, dict) and "name" in function:
                            function_id = f"{capability_id}-function-{function.get('id', function['name'].lower().replace(' ', '-'))}"
                            
                            # Check for specifications
                            specifications = []
                            if "specifications" in function:
                                if isinstance(function["specifications"], list):
                                    specifications = function["specifications"]
                                elif isinstance(function["specifications"], dict) and "items" in function["specifications"]:
                                    specifications = function["specifications"]["items"]
                                elif isinstance(function["specifications"], dict):
                                    specifications = [function["specifications"]]
                            
                            has_specs = len(specifications) > 0
                            
                            nodes.append({
                                "id": function_id,
                                "name": function["name"],
                                "type": "function",
                                "description": function.get("description", ""),
                                "parent": capability_id,
                                "level": 4,
                                "expandable": has_specs,
                                "has_children": has_specs
                            })
                            
                            # Add link from capability to function
                            links.append({
                                "source": capability_id,
                                "target": function_id,
                                "type": "has_function"
                            })
                            
                            # Add specification nodes (level 5)
                            for specification in specifications:
                                if isinstance(specification, dict) and "name" in specification:
                                    specification_id = f"{function_id}-specification-{specification.get('id', specification['name'].lower().replace(' ', '-'))}"
                                    
                                    # Check for integrations - handle both array and direct object
                                    integrations = []
                                    if "integration" in specification:
                                        # Handle case where integration is a direct object, not in an array
                                        if isinstance(specification["integration"], dict):
                                            integrations = [specification["integration"]]
                                        elif isinstance(specification["integration"], list):
                                            integrations = specification["integration"]
                                    elif "integrations" in specification:
                                        if isinstance(specification["integrations"], list):
                                            integrations = specification["integrations"]
                                        elif isinstance(specification["integrations"], dict) and "items" in specification["integrations"]:
                                            integrations = specification["integrations"]["items"]
                                    
                                    has_integrations = len(integrations) > 0
                                    
                                    # Set has_children correctly based on actual content
                                    spec_has_children = has_integrations
                                    
                                    nodes.append({
                                        "id": specification_id,
                                        "name": specification["name"],
                                        "type": "specification",
                                        "description": specification.get("description", ""),
                                        "parent": function_id,
                                        "level": 5,
                                        "expandable": spec_has_children,
                                        "has_children": spec_has_children
                                    })
                                    
                                    # Add link from function to specification
                                    links.append({
                                        "source": function_id,
                                        "target": specification_id,
                                        "type": "has_specification"
                                    })
                                    
                                    # Add integration nodes (level 6)
                                    for integration in integrations:
                                        if isinstance(integration, dict) and "name" in integration:
                                            integration_id = f"{specification_id}-integration-{integration.get('id', integration['name'].lower().replace(' ', '-'))}"
                                            
                                            # Check for techniques
                                            techniques = []
                                            if "techniques" in integration:
                                                if isinstance(integration["techniques"], list):
                                                    techniques = integration["techniques"]
                                                elif isinstance(integration["techniques"], dict) and "items" in integration["techniques"]:
                                                    techniques = integration["techniques"]["items"]
                                                elif isinstance(integration["techniques"], dict):
                                                    techniques = [integration["techniques"]]
                                            
                                            has_techniques = len(techniques) > 0
                                            
                                            nodes.append({
                                                "id": integration_id,
                                                "name": integration["name"],
                                                "type": "integration",
                                                "description": integration.get("description", ""),
                                                "parent": specification_id,
                                                "level": 6,
                                                "expandable": has_techniques,
                                                "has_children": has_techniques
                                            })
                                            
                                            # Add link from specification to integration
                                            links.append({
                                                "source": specification_id,
                                                "target": integration_id,
                                                "type": "has_integration"
                                            })
                                            
                                            # Add technique nodes (level 7)
                                            for technique in techniques:
                                                if isinstance(technique, dict) and "name" in technique:
                                                    technique_id = f"{integration_id}-technique-{technique.get('id', technique['name'].lower().replace(' ', '-'))}"
                                                    
                                                    # Check for applications
                                                    applications = []
                                                    if "applications" in technique:
                                                        if isinstance(technique["applications"], list):
                                                            applications = technique["applications"]
                                                        elif isinstance(technique["applications"], dict) and "items" in technique["applications"]:
                                                            applications = technique["applications"]["items"]
                                                        elif isinstance(technique["applications"], dict):
                                                            applications = [technique["applications"]]
                                                    
                                                    has_applications = len(applications) > 0
                                                    
                                                    nodes.append({
                                                        "id": technique_id,
                                                        "name": technique["name"],
                                                        "type": "technique",
                                                        "description": technique.get("description", ""),
                                                        "parent": integration_id,
                                                        "level": 7,
                                                        "expandable": has_applications,
                                                        "has_children": has_applications
                                                    })
                                                    
                                                    # Add link from integration to technique
                                                    links.append({
                                                        "source": integration_id,
                                                        "target": technique_id,
                                                        "type": "has_technique"
                                                    })
                                                    
                                                    # Add application nodes (level 8)
                                                    for application in applications:
                                                        if isinstance(application, dict) and "name" in application:
                                                            application_id = f"{technique_id}-application-{application.get('id', application['name'].lower().replace(' ', '-'))}"
                                                            
                                                            # Check for inputs
                                                            inputs = []
                                                            if "inputs" in application:
                                                                if isinstance(application["inputs"], list):
                                                                    inputs = application["inputs"]
                                                                elif isinstance(application["inputs"], dict) and "items" in application["inputs"]:
                                                                    inputs = application["inputs"]["items"]
                                                                elif isinstance(application["inputs"], dict):
                                                                    inputs = [application["inputs"]]
                                                            
                                                            has_inputs = len(inputs) > 0
                                                            
                                                            nodes.append({
                                                                "id": application_id,
                                                                "name": application["name"],
                                                                "type": "application",
                                                                "description": application.get("description", ""),
                                                                "parent": technique_id,
                                                                "level": 8,
                                                                "expandable": has_inputs,
                                                                "has_children": has_inputs
                                                            })
                                                            
                                                            # Add link from technique to application
                                                            links.append({
                                                                "source": technique_id,
                                                                "target": application_id,
                                                                "type": "has_application"
                                                            })
                                                            
                                                            # Add input nodes (level 9)
                                                            for input_item in inputs:
                                                                if isinstance(input_item, dict) and "name" in input_item:
                                                                    input_id = f"{application_id}-input-{input_item.get('id', input_item['name'].lower().replace(' ', '-'))}"
                                                                    
                                                                    # Check for outputs
                                                                    outputs = []
                                                                    if "outputs" in input_item:
                                                                        if isinstance(input_item["outputs"], list):
                                                                            outputs = input_item["outputs"]
                                                                        elif isinstance(input_item["outputs"], dict) and "items" in input_item["outputs"]:
                                                                            outputs = input_item["outputs"]["items"]
                                                                        elif isinstance(input_item["outputs"], dict):
                                                                            outputs = [input_item["outputs"]]
                                                                    
                                                                    has_outputs = len(outputs) > 0
                                                                    
                                                                    nodes.append({
                                                                        "id": input_id,
                                                                        "name": input_item["name"],
                                                                        "type": "input",
                                                                        "description": input_item.get("description", ""),
                                                                        "parent": application_id,
                                                                        "level": 9,
                                                                        "expandable": has_outputs,
                                                                        "has_children": has_outputs
                                                                    })
                                                                    
                                                                    # Add link from application to input
                                                                    links.append({
                                                                        "source": application_id,
                                                                        "target": input_id,
                                                                        "type": "has_input"
                                                                    })
                                                                    
                                                                    # Add output nodes (level 10)
                                                                    for output in outputs:
                                                                        if isinstance(output, dict) and "name" in output:
                                                                            output_id = f"{input_id}-output-{output.get('id', output['name'].lower().replace(' ', '-'))}"
                                                                            
                                                                            nodes.append({
                                                                                "id": output_id,
                                                                                "name": output["name"],
                                                                                "type": "output",
                                                                                "description": output.get("description", ""),
                                                                                "parent": input_id,
                                                                                "level": 10,
                                                                                "expandable": False,
                                                                                "has_children": False
                                                                            })
                                                                            
                                                                            # Add link from input to output
                                                                            links.append({
                                                                                "source": input_id,
                                                                                "target": output_id,
                                                                                "type": "has_output"
                                                                            })
    
    app.logger.info(f"Built graph with {len(nodes)} nodes and {len(links)} links")
    return {"nodes": nodes, "links": links}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/graph')
def graph():
    try:
        graph_data = build_graph_data()
        app.logger.info(f"Returning graph with {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} links")
        return jsonify(graph_data)
    except Exception as e:
        app.logger.error(f"Error generating graph data: {str(e)}")
        return jsonify({"error": str(e), "nodes": [], "links": []}), 500

@app.route('/api/details/<node_id>')
def node_details(node_id):
    """Fetches detailed information about a specific node."""
    try:
        app.logger.info(f"Getting details for node: {node_id}")
        
        # Get data sources
        root_data = get_root_data()
        components = get_components()
        subcomponents = get_subcomponents()
        
        # Check if it's the root node
        if node_id == root_data["id"]:
            app.logger.info(f"Returning root node details: {root_data['name']}")
            return jsonify(root_data)
        
        # Check if it's a component
        if node_id in components:
            app.logger.info(f"Returning component details: {components[node_id]['name']}")
            return jsonify(components[node_id])
        
        # Check if it's a subcomponent
        if node_id in subcomponents:
            app.logger.info(f"Returning subcomponent details: {subcomponents[node_id]['name']}")
            return jsonify(subcomponents[node_id])
        
        # For other nodes, search through the graph
        graph_data = build_graph_data()
        for node in graph_data["nodes"]:
            if node["id"] == node_id:
                app.logger.info(f"Returning node details from graph: {node['name']}")
                return jsonify(node)
        
        app.logger.warning(f"Node not found: {node_id}")
        return jsonify({"error": "Node not found", "id": node_id, "name": "Unknown Node", "description": "Node details not found."}), 404
    except Exception as e:
        app.logger.error(f"Error getting node details: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/hierarchy-path/<node_id>')
def hierarchy_path(node_id):
    """Returns the path from root to the specified node."""
    graph_data = build_graph_data()
    
    # Find the node
    target_node = None
    for node in graph_data["nodes"]:
        if node["id"] == node_id:
            target_node = node
            break
    
    if not target_node:
        return jsonify({"error": "Node not found"}), 404
    
    # Build the path
    path = [{"id": target_node["id"], "name": target_node["name"], "type": target_node["type"]}]
    
    # Traverse up the hierarchy
    current_node = target_node
    while "parent" in current_node:
        parent_id = current_node["parent"]
        parent_node = None
        
        for node in graph_data["nodes"]:
            if node["id"] == parent_id:
                parent_node = node
                break
        
        if parent_node:
            path.insert(0, {"id": parent_node["id"], "name": parent_node["name"], "type": parent_node["type"]})
            current_node = parent_node
        else:
            break
    
    return jsonify({"path": path})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"Starting AI Alignment Visualization on http://localhost:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True) 
# AI Alignment Templates

This directory contains template files that define the structure of components in the AI alignment architecture. The templates establish a clear hierarchical structure while allowing for connections between any nodes in the architecture, regardless of their position in the hierarchy.

## Hierarchical Structure

The architecture follows a strict parent-child hierarchy:

1. **Component Group** - Top-level container (e.g., AI Alignment)
2. **Components** - Major functional areas (e.g., Technical Safeguards)
3. **Subcomponents** - Specific implementation elements
4. **Capabilities** - What the subcomponent can do
5. **Functions** - How the capability is implemented
6. **Specifications** - Technical details of the function
7. **Integration** - How the specification connects with other components
8. **Techniques** - Specific methods to implement the integration
9. **Applications** - Concrete implementations with inputs/outputs

## Cross-Connections

While the structure follows a hierarchy, any node can connect to any other node through the `cross_connections` field. Each connection specifies:

- `source_id`: The ID of the source node
- `target_id`: The ID of the target node
- `type`: The type of relationship (e.g., "depends_on", "enables", "alternative_to")
- `description`: Description of the relationship

These cross-connections allow for representing complex interdependencies within the architecture while maintaining a clear hierarchical structure for navigation.

## Considerations as Metadata

Considerations are no longer represented as nodes in the hierarchy. Instead, they are included as metadata attached to other nodes through the `metadata.considerations` field. This allows for documenting important considerations without cluttering the node hierarchy.

## Template Files

- **component-group-template.json**: Defines the top level of the hierarchy
- **component-template.json**: Defines a component within a component group
- **subcomponent-template.json**: Defines a subcomponent and its child elements down to applications

## Usage Guidelines

1. Start with the appropriate template based on what you're defining
2. Fill in the required fields for each level in the hierarchy
3. Use the `cross_connections` field to define relationships with other nodes
4. Document considerations in the `metadata.considerations` field
5. Ensure all IDs are unique and follow a consistent naming pattern

## Example Node IDs

To maintain consistency, use the following ID format for each level:
- Component Group: `ai-alignment`
- Component: `component-id`
- Subcomponent: `subcomponent-id`
- Capability: `capability-id`
- Function: `function-id`
- Specification: `specification-id`
- Integration: `integration-id`
- Technique: `technique-id`
- Application: `application-id`

For cross-connections, reference the exact ID of the target node.

## Network Model Structure

The network model follows a hierarchical structure:

1. **Component Groups** contain Components
2. **Components** contain Subcomponents
3. **Subcomponents** contain detailed implementation elements:
   - Capabilities
   - Functions
   - Techniques
   - Applications
   - Input/Output Specifications
   - Considerations

## Cross-cutting Elements

Several elements create cross-cutting connections in the network:

- **Considerations**: Appear at component and subcomponent levels, creating vertical connections through `derives_from_integration_considerations` and horizontal connections through `addressed_by_techniques`
- **Capabilities**: Connect components to subcomponents and create horizontal connections across subcomponents
- **Functions**: Connect from component to subcomponent levels and horizontally across subcomponents
- **Inputs/Outputs**: Define the specific data exchanges between nodes

## Navigational Depth Requirements

For proper visualization, each level must include specific references:

1. **Component Groups**:
   - Must list all components they contain
   
2. **Components**:
   - Must list all subcomponents they contain
   - Must define capabilities and functions duplicated from overview section
   - Must define integration approaches and considerations

3. **Subcomponents**:
   - Functions must reference capabilities from other subcomponents via `enabled_by_capabilities`
   - Must define techniques with their applications
   - Must define implementation considerations derived from component considerations
   - Must define input/output specifications
   - Must define relationships with other subcomponents

## Visualization Guidance

In a network visualization:

1. **Considerations** would likely be displayed:
   - In a detail panel when a node is clicked
   - As color coding or filter options across the network
   - As supplementary information in a separate tab

2. **Bidirectional References** create a fully connected network where:
   - Vertical connections show containment relationships
   - Horizontal connections show interactions via shared inputs/outputs

## Required Fields for Network Visualization

The following fields are critical for proper network model visualization:

- IDs must follow the pattern `parent-id.element-id`
- All references to other elements must use full IDs
- Cross-cutting references are required for proper network connectivity 
"""
Interactive MCP Resources and Prompts for NetIntel-OCR
"""

from typing import Dict, Any, List, Optional
from mcp import Resource, Prompt, resource, prompt
from datetime import datetime
import json


# ==================== Interactive Resources ====================

@resource("document://explore/{document_id}")
async def explore_document(document_id: str) -> Dict[str, Any]:
    """
    Interactive document exploration with navigation

    Provides:
    - Document metadata and content
    - Page navigation
    - Search within document
    - Entity exploration
    - Version history
    """

    # This would load actual document data
    # For now, return mock interactive data

    return {
        "document_id": document_id,
        "metadata": {
            "title": "Network Configuration Guide",
            "pages": 45,
            "created": datetime.utcnow().isoformat(),
            "type": "pdf",
        },
        "navigation": {
            "current_page": 1,
            "total_pages": 45,
            "sections": [
                {"title": "Introduction", "page": 1},
                {"title": "Network Topology", "page": 5},
                {"title": "Security Configuration", "page": 15},
                {"title": "Troubleshooting", "page": 35},
            ],
        },
        "entities": {
            "devices": 23,
            "ip_addresses": 45,
            "vlans": 12,
        },
        "actions": [
            "next_page",
            "previous_page",
            "search",
            "extract_entities",
            "view_diagrams",
            "view_tables",
        ],
    }


@resource("topology://visualize/{document_id}")
async def visualize_topology(document_id: str) -> Dict[str, Any]:
    """
    Interactive network topology visualization

    Features:
    - 3D network visualization
    - Device details on hover
    - Path highlighting
    - Traffic flow animation
    - Export capabilities
    """

    return {
        "document_id": document_id,
        "visualization": {
            "type": "network_topology",
            "nodes": [
                {
                    "id": "router1",
                    "label": "Core-Router-01",
                    "type": "router",
                    "x": 100, "y": 100, "z": 0,
                    "properties": {"vendor": "Cisco", "model": "ASR 9000"},
                },
                {
                    "id": "switch1",
                    "label": "Dist-Switch-01",
                    "type": "switch",
                    "x": 200, "y": 150, "z": 0,
                    "properties": {"vendor": "Juniper", "ports": 48},
                },
            ],
            "edges": [
                {
                    "source": "router1",
                    "target": "switch1",
                    "label": "10Gbps",
                    "type": "fiber",
                },
            ],
        },
        "interactions": {
            "zoom": True,
            "pan": True,
            "rotate": True,
            "select": True,
            "highlight_paths": True,
        },
        "export_formats": ["svg", "png", "json", "graphml"],
    }


@resource("kg://explore/{document_id}")
async def explore_knowledge_graph(document_id: str) -> Dict[str, Any]:
    """
    Interactive knowledge graph exploration

    Features:
    - Graph navigation
    - Entity details
    - Relationship exploration
    - Query builder
    - Visual filtering
    """

    return {
        "document_id": document_id,
        "graph": {
            "total_entities": 156,
            "total_relationships": 289,
            "entity_types": ["Router", "Switch", "Firewall", "Server", "VLAN"],
            "relationship_types": ["CONNECTS_TO", "SECURED_BY", "ROUTES_TO"],
        },
        "current_view": {
            "center_entity": "Core-Router-01",
            "depth": 2,
            "visible_nodes": 15,
            "visible_edges": 22,
        },
        "filters": {
            "entity_types": [],
            "relationship_types": [],
            "properties": {},
        },
        "actions": [
            "expand_node",
            "collapse_node",
            "filter_by_type",
            "find_paths",
            "run_query",
            "export_subgraph",
        ],
    }


@resource("milvus://collection/{collection_name}")
async def explore_milvus_collection(collection_name: str) -> Dict[str, Any]:
    """
    Interactive Milvus collection exploration with schema and stats

    Provides:
    - Collection schema
    - Statistics and metrics
    - Sample data
    - Index information
    - Query interface
    """

    return {
        "collection_name": collection_name,
        "schema": {
            "fields": [
                {"name": "id", "type": "INT64", "is_primary": True},
                {"name": "document_id", "type": "VARCHAR", "max_length": 256},
                {"name": "embedding", "type": "FLOAT_VECTOR", "dim": 768},
                {"name": "content", "type": "VARCHAR", "max_length": 65535},
                {"name": "metadata", "type": "JSON"},
            ],
            "description": "Document embeddings collection",
            "enable_dynamic_field": False,
        },
        "statistics": {
            "row_count": 150000,
            "index_type": "IVF_FLAT",
            "metric_type": "IP",
            "loaded": True,
            "partitions": 4,
        },
        "sample_data": [
            {
                "id": 1,
                "document_id": "doc_123",
                "content": "Sample content...",
                "score": 0.95,
            },
        ],
        "actions": [
            "search",
            "insert",
            "delete",
            "update_index",
            "load",
            "release",
        ],
    }


@resource("milvus://search/{collection_name}")
async def milvus_search_interface(collection_name: str) -> Dict[str, Any]:
    """
    Interactive search interface for Milvus collections

    Features:
    - Query builder
    - Filter constructor
    - Result visualization
    - Export capabilities
    """

    return {
        "collection_name": collection_name,
        "search_interface": {
            "query_types": ["vector", "scalar", "hybrid"],
            "current_query": {
                "type": "vector",
                "text": "",
                "filters": {},
                "limit": 10,
            },
            "available_fields": ["document_id", "content", "metadata"],
            "filter_options": {
                "document_id": "string",
                "page_number": "int",
                "confidence": "float",
            },
        },
        "recent_searches": [
            {
                "query": "network security",
                "results": 25,
                "timestamp": datetime.utcnow().isoformat(),
            },
        ],
        "saved_queries": [],
        "export_formats": ["json", "csv", "excel"],
    }


@resource("milvus://visualize/{collection_name}")
async def visualize_vector_space(collection_name: str) -> Dict[str, Any]:
    """
    3D visualization of vector embeddings in collection

    Features:
    - 3D scatter plot
    - Clustering visualization
    - Similarity regions
    - Interactive exploration
    """

    return {
        "collection_name": collection_name,
        "visualization": {
            "type": "3d_scatter",
            "dimensions_reduced": 3,  # From 768 to 3 using UMAP
            "points": [
                {
                    "id": 1,
                    "x": 0.5, "y": 0.3, "z": 0.2,
                    "cluster": 0,
                    "label": "Document 1",
                },
                {
                    "id": 2,
                    "x": 0.6, "y": 0.35, "z": 0.25,
                    "cluster": 0,
                    "label": "Document 2",
                },
            ],
            "clusters": [
                {"id": 0, "label": "Network Configuration", "size": 45},
                {"id": 1, "label": "Security Policies", "size": 32},
                {"id": 2, "label": "Troubleshooting", "size": 28},
            ],
        },
        "controls": {
            "zoom": True,
            "rotate": True,
            "pan": True,
            "select_cluster": True,
            "highlight_similar": True,
        },
        "metrics": {
            "silhouette_score": 0.72,
            "davies_bouldin": 0.58,
            "cluster_separation": "good",
        },
    }


# ==================== Contextual Prompts ====================

@prompt()
async def contextual_analysis(
    document_ids: List[str],
    focus_area: str,
    previous_context: Optional[str] = None
) -> str:
    """Generate contextual analysis prompt with memory"""

    base_prompt = f"""
    Analyze the following documents with focus on {focus_area}.

    Documents to analyze: {', '.join(document_ids)}

    Key aspects to consider:
    1. Identify main themes related to {focus_area}
    2. Extract relevant configurations and settings
    3. Note any inconsistencies or issues
    4. Provide actionable recommendations
    """

    if previous_context:
        base_prompt += f"\n\nPrevious context:\n{previous_context}\n"
        base_prompt += "\nBuild upon the previous analysis and provide deeper insights."

    base_prompt += """

    Please provide:
    - Executive summary (2-3 sentences)
    - Key findings (bullet points)
    - Recommendations (prioritized list)
    - Areas requiring further investigation
    """

    return base_prompt


@prompt()
async def synthesize_documents(
    document_ids: List[str],
    synthesis_type: str = "summary"  # summary|comparison|timeline
) -> str:
    """Synthesize information across multiple documents"""

    prompts = {
        "summary": f"""
        Synthesize the key information from documents: {', '.join(document_ids)}

        Create a comprehensive summary that:
        1. Identifies common themes across all documents
        2. Highlights unique information from each document
        3. Resolves any conflicting information
        4. Provides a unified view of the topic

        Structure:
        - Overview (1 paragraph)
        - Key themes (bullet points)
        - Document-specific insights
        - Synthesis and conclusions
        """,

        "comparison": f"""
        Compare and contrast documents: {', '.join(document_ids)}

        Analysis framework:
        1. Similarities:
           - Common configurations
           - Shared approaches
           - Consistent policies

        2. Differences:
           - Unique features
           - Conflicting recommendations
           - Version-specific changes

        3. Evaluation:
           - Best practices identified
           - Recommended approach
           - Items requiring clarification
        """,

        "timeline": f"""
        Create a timeline of changes across documents: {', '.join(document_ids)}

        Timeline should include:
        1. Chronological ordering of documents
        2. Key changes between versions
        3. Evolution of configurations
        4. Deprecated features
        5. New additions

        Format as:
        [Date] - [Document] - [Key Changes]
        """,
    }

    return prompts.get(synthesis_type, prompts["summary"])


@prompt()
async def troubleshooting_guide(
    issue_description: str,
    relevant_documents: List[str]
) -> str:
    """Generate troubleshooting guide from documentation"""

    return f"""
    Create a troubleshooting guide for the following issue:

    Issue: {issue_description}

    Reference documents: {', '.join(relevant_documents)}

    Guide structure:

    1. Problem Identification
       - Symptoms
       - Affected components
       - Error messages

    2. Root Cause Analysis
       - Possible causes (ranked by likelihood)
       - Diagnostic steps
       - Required information to gather

    3. Resolution Steps
       - Immediate actions
       - Step-by-step resolution
       - Verification procedures

    4. Prevention
       - Best practices
       - Monitoring recommendations
       - Configuration changes

    5. Escalation Path
       - When to escalate
       - Information to provide
       - Contact points

    Use specific examples and commands from the documentation where applicable.
    """


@prompt()
async def security_audit_prompt(
    document_ids: List[str],
    compliance_standards: List[str]
) -> str:
    """Generate security audit prompt"""

    return f"""
    Perform a security audit of the network configuration based on:

    Documents: {', '.join(document_ids)}
    Compliance Standards: {', '.join(compliance_standards)}

    Audit Areas:

    1. Access Control
       - Authentication mechanisms
       - Authorization policies
       - Privilege escalation risks

    2. Network Security
       - Firewall configurations
       - Network segmentation
       - Encrypted communications

    3. Data Protection
       - Data classification
       - Encryption at rest/transit
       - Backup procedures

    4. Monitoring & Logging
       - Audit trail completeness
       - Log retention policies
       - Security monitoring

    5. Incident Response
       - Response procedures
       - Recovery capabilities
       - Communication protocols

    For each area:
    - Current state assessment
    - Compliance gaps
    - Risk rating (Critical/High/Medium/Low)
    - Remediation recommendations
    - Implementation priority

    Provide an overall security score and executive summary.
    """


@prompt()
async def network_design_review(
    topology_data: Dict[str, Any],
    requirements: Dict[str, Any]
) -> str:
    """Generate network design review prompt"""

    return f"""
    Review the network design against specified requirements:

    Topology Summary:
    - Devices: {topology_data.get('device_count', 'Unknown')}
    - Zones: {topology_data.get('zones', [])}
    - Redundancy Level: {topology_data.get('redundancy', 'Unknown')}

    Requirements:
    {json.dumps(requirements, indent=2)}

    Review Criteria:

    1. Architecture Assessment
       - Scalability analysis
       - Performance bottlenecks
       - Single points of failure
       - Redundancy adequacy

    2. Security Evaluation
       - Zone isolation
       - Traffic flow analysis
       - Security control placement
       - Access control points

    3. Performance Analysis
       - Bandwidth utilization
       - Latency considerations
       - Load distribution
       - QoS implementation

    4. Compliance Check
       - Industry standards adherence
       - Best practice alignment
       - Regulatory requirements

    5. Recommendations
       - Critical improvements
       - Optimization opportunities
       - Future-proofing suggestions
       - Cost-benefit analysis

    Provide scores for each criterion and an overall design rating.
    """
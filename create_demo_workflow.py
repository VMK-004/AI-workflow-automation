#!/usr/bin/env python3
"""
Video Demo Workflow Creation Script
Creates a complete RAG Customer Support workflow for video demonstration
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your deployment URL
USERNAME = "demo_user"
PASSWORD = "demo123"

def main():
    print("🎬 Creating Video Demo Workflow...\n")

    # Step 1: Register/Login
    print("1️⃣ Authenticating...")
    try:
        # Try to register first
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": USERNAME,
                "email": f"{USERNAME}@example.com",
                "password": PASSWORD
            }
        )
        if register_response.status_code == 201:
            print("   ✅ User registered")
            token = register_response.json()["access_token"]
        else:
            # User already exists, login instead
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": USERNAME, "password": PASSWORD}
            )
            login_response.raise_for_status()
            token = login_response.json()["access_token"]
            print("   ✅ User logged in")
    except Exception as e:
        # Fallback to login
        try:
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": USERNAME, "password": PASSWORD}
            )
            login_response.raise_for_status()
            token = login_response.json()["access_token"]
            print("   ✅ User logged in")
        except Exception as e2:
            print(f"   ❌ Authentication failed: {str(e2)}")
            print(f"   Please check if the server is running at {BASE_URL}")
            sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Create Workflow
    print("\n2️⃣ Creating workflow...")
    try:
        workflow_response = requests.post(
            f"{BASE_URL}/api/workflows",
            headers=headers,
            json={
                "name": "Resume-Job Match Assistant",
                "description": "Matches resumes with job descriptions using vector search and AI analysis"
            }
        )
        workflow_response.raise_for_status()
        workflow = workflow_response.json()
        workflow_id = workflow["id"]
        print(f"   ✅ Workflow created: {workflow['name']} (ID: {workflow_id})")
    except Exception as e:
        print(f"   ❌ Failed to create workflow: {str(e)}")
        sys.exit(1)

    # Step 3: Create Vector Collection (for FAISS search)
    print("\n3️⃣ Creating vector collection...")
    collection_name = "resume_database"
    try:
        collection_response = requests.post(
            f"{BASE_URL}/api/vectors/collections",
            headers=headers,
            json={
                "name": collection_name,
                "dimension": 384  # sentence-transformers default
            }
        )
        if collection_response.status_code == 201:
            print("   ✅ Vector collection created")
            print(f"   💡 You can upload your resume using:")
            print(f"      POST /api/vectors/collections/{collection_name}/upload")
            print(f"      (Supports PDF, DOCX, and TXT files)")
            print(f"   💡 Or add text directly:")
            print(f"      POST /api/vectors/collections/{collection_name}/documents")
        else:
            print(f"   ⚠️  Collection may already exist (status: {collection_response.status_code})")
            print(f"   💡 Collection '{collection_name}' is ready for your resume upload")
    except Exception as e:
        print(f"   ⚠️  Collection setup issue: {str(e)}")

    # Step 4: Create Nodes
    print("\n4️⃣ Creating workflow nodes...")

    nodes = {}
    
    # Node 1: FAISS Search
    print("   Creating FAISS Search node...")
    try:
        search_node_response = requests.post(
            f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
            headers=headers,
            json={
                "name": "Search Resume",
                "node_type": "faiss_search",
                "config": {
                    "collection_name": collection_name,
                    "query": "{input.job_description}",
                    "top_k": 5
                },
                "position_x": 100,
                "position_y": 200
            }
        )
        search_node_response.raise_for_status()
        search_node = search_node_response.json()
        nodes["search"] = search_node
        print(f"      ✅ Node: {search_node['name']} (ID: {search_node['id']})")
    except Exception as e:
        print(f"      ❌ Failed to create search node: {str(e)}")
        sys.exit(1)

    # Node 2: LLM Call
    print("   Creating LLM Call node...")
    try:
        llm_node_response = requests.post(
            f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
            headers=headers,
            json={
                "name": "Analyze Match",
                "node_type": "llm_call",
                "config": {
                    "prompt_template": """You are a professional resume analyst. Analyze how well a candidate's resume matches a job description.

Job Description:
{input.job_description}

Relevant Resume Sections:
{input.Search Resume.results}

Provide a comprehensive analysis:
1. **Match Score**: Rate from 1-10 how well the resume matches the job
2. **Key Strengths**: List top 3-5 matching qualifications, skills, or experiences
3. **Relevant Experience**: Extract and highlight experience relevant to the job
4. **Skills Match**: Identify matching technical skills, tools, and certifications
5. **Gaps**: Mention any important requirements missing from the resume
6. **Recommendations**: Suggest improvements to better align with the job

Format your response clearly with headers for each section.""",
                    "temperature": 0.7,
                    "max_tokens": 800
                },
                "position_x": 400,
                "position_y": 200
            }
        )
        llm_node_response.raise_for_status()
        llm_node = llm_node_response.json()
        nodes["llm"] = llm_node
        print(f"      ✅ Node: {llm_node['name']} (ID: {llm_node['id']})")
    except Exception as e:
        print(f"      ❌ Failed to create LLM node: {str(e)}")
        sys.exit(1)

    # Node 3: HTTP Request (Optional - can be removed if not needed)
    print("   Creating HTTP Request node...")
    try:
        http_node_response = requests.post(
            f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
            headers=headers,
            json={
                "name": "Send Results",
                "node_type": "http_request",
                "config": {
                    "method": "POST",
                    "url": "https://httpbin.org/post",  # Public testing endpoint - replace with your webhook
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "job_description": "{input.job_description}",
                        "match_analysis": "{input.Analyze Match.output}",
                        "timestamp": "{{now}}"
                    }
                },
                "position_x": 700,
                "position_y": 200
            }
        )
        http_node_response.raise_for_status()
        http_node = http_node_response.json()
        nodes["http"] = http_node
        print(f"      ✅ Node: {http_node['name']} (ID: {http_node['id']})")
    except Exception as e:
        print(f"      ❌ Failed to create HTTP node: {str(e)}")
        sys.exit(1)

    # Node 4: DB Write
    print("   Creating DB Write node...")
    try:
        db_node_response = requests.post(
            f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
            headers=headers,
            json={
                "name": "Save Match Analysis",
                "node_type": "db_write",
                "config": {
                    "table": "resume_matches",
                    "data": {
                        "job_description": "{input.job_description}",
                        "match_analysis": "{input.Analyze Match.output}",
                        "resume_sections": "{input.Search Resume.results}",
                        "status": "completed",
                        "created_at": "{{now}}"
                    }
                },
                "position_x": 1000,
                "position_y": 200
            }
        )
        db_node_response.raise_for_status()
        db_node = db_node_response.json()
        nodes["db"] = db_node
        print(f"      ✅ Node: {db_node['name']} (ID: {db_node['id']})")
    except Exception as e:
        print(f"      ❌ Failed to create DB node: {str(e)}")
        sys.exit(1)

    # Step 5: Create Edges (Connect Nodes)
    print("\n5️⃣ Connecting nodes...")
    
    edges_created = []
    
    # Search → LLM
    try:
        edge1_response = requests.post(
            f"{BASE_URL}/api/workflows/{workflow_id}/edges",
            headers=headers,
            json={
                "source_node_id": nodes["search"]["id"],
                "target_node_id": nodes["llm"]["id"]
            }
        )
        edge1_response.raise_for_status()
        edges_created.append((nodes["search"]["name"], nodes["llm"]["name"]))
        print(f"   ✅ Connected: {nodes['search']['name']} → {nodes['llm']['name']}")
    except Exception as e:
        print(f"   ❌ Failed to create edge: {str(e)}")

    # LLM → HTTP (optional)
    try:
        edge2_response = requests.post(
            f"{BASE_URL}/api/workflows/{workflow_id}/edges",
            headers=headers,
            json={
                "source_node_id": nodes["llm"]["id"],
                "target_node_id": nodes["http"]["id"]
            }
        )
        edge2_response.raise_for_status()
        edges_created.append((nodes["llm"]["name"], nodes["http"]["name"]))
        print(f"   ✅ Connected: {nodes['llm']['name']} → {nodes['http']['name']}")
    except Exception as e:
        print(f"   ⚠️  HTTP node connection skipped: {str(e)}")

    # LLM → DB
    try:
        edge3_response = requests.post(
            f"{BASE_URL}/api/workflows/{workflow_id}/edges",
            headers=headers,
            json={
                "source_node_id": nodes["llm"]["id"],
                "target_node_id": nodes["db"]["id"]
            }
        )
        edge3_response.raise_for_status()
        edges_created.append((nodes["llm"]["name"], nodes["db"]["name"]))
        print(f"   ✅ Connected: {nodes['llm']['name']} → {nodes['db']['name']}")
    except Exception as e:
        print(f"   ❌ Failed to create edge: {str(e)}")

    # Step 6: Verify Workflow
    print("\n6️⃣ Verifying workflow...")
    try:
        nodes_response = requests.get(
            f"{BASE_URL}/api/workflows/{workflow_id}/nodes",
            headers=headers
        )
        nodes_response.raise_for_status()
        edges_response = requests.get(
            f"{BASE_URL}/api/workflows/{workflow_id}/edges",
            headers=headers
        )
        edges_response.raise_for_status()

        nodes_list = nodes_response.json()
        edges_list = edges_response.json()

        print(f"   ✅ Workflow verification:")
        print(f"      • Nodes: {len(nodes_list)}")
        print(f"      • Edges: {len(edges_list)}")
    except Exception as e:
        print(f"   ⚠️  Verification issue: {str(e)}")

    # Final Summary
    print("\n" + "="*60)
    print("🎉 WORKFLOW CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Workflow Summary:")
    print(f"   Name: Resume-Job Match Assistant")
    print(f"   ID: {workflow_id}")
    print(f"\n🔗 Nodes ({len(nodes)}):")
    for node_key, node in nodes.items():
        print(f"   • {node['name']} ({node['node_type']})")
    print(f"\n🔗 Connections ({len(edges_created)}):")
    for source, target in edges_created:
        print(f"   • {source} → {target}")

    print(f"\n🚀 Next Steps:")
    print(f"   1. Open the workflow editor in your frontend")
    print(f"   2. Execute the workflow with the command below")
    print(f"\n📝 Execute Command:")
    print(f"""
curl -X POST "{BASE_URL}/api/workflows/{workflow_id}/execute" \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json" \\
  -d '{{"input_data": {{"job_description": "Looking for a Full-Stack Developer with 3+ years experience in React, Node.js, and PostgreSQL. Must have experience with REST APIs and cloud deployment."}}}}'
""")
    
    print(f"\n💡 Or use Python:")
    print(f"""
import requests
response = requests.post(
    "{BASE_URL}/api/workflows/{workflow_id}/execute",
    headers={{"Authorization": "Bearer {token}"}},
    json={{"input_data": {{
        "job_description": "Looking for a Full-Stack Developer with 3+ years experience in React, Node.js, and PostgreSQL. Must have experience with REST APIs and cloud deployment."
    }}}}
)
print(response.json())
""")
    
    print(f"\n📋 Example Job Descriptions to Test:")
    print(f"   • Software Engineer: React, TypeScript, Node.js, PostgreSQL")
    print(f"   • Data Scientist: Python, Machine Learning, SQL, Statistics")
    print(f"   • DevOps Engineer: Docker, Kubernetes, AWS, CI/CD")
    print(f"\n💡 Remember: Upload your resume first to the '{collection_name}' collection!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    if len(sys.argv) > 2:
        USERNAME = sys.argv[2]
    if len(sys.argv) > 3:
        PASSWORD = sys.argv[3]
    
    main()


# 🎥 Video Demo - Resume-Job Match Workflow

## 📋 Overview

This guide shows how to create a **Resume-Job Match Assistant** workflow that demonstrates all 4 node types in action. The workflow analyzes how well a resume matches a job description using vector search and AI analysis.

### Workflow Scenario: "Resume-Job Match Assistant"

**Use Case:** Match resumes with job descriptions by:
1. Searching resume content in vector database
2. Using AI to analyze match quality
3. Extracting relevant skills and experience
4. Saving results for tracking

**Flow:**
```
Job Description Input
    ↓
FAISS Search (find relevant resume sections)
    ↓
LLM Call (analyze match & extract insights)
    ↓
HTTP Request (optional: send to external service)
    ↓
DB Write (save match analysis to database)
```

---

## 🚀 Quick Setup Script

Run this Python script to create the complete workflow:

```bash
python create_demo_workflow.py
```

Or with custom URL:
```bash
python create_demo_workflow.py https://ai-workflow-automation-ikld.onrender.com
```

---

## 📝 Step-by-Step Guide

### Step 1: Upload Your Resume

Before creating the workflow, upload your resume to the vector database:

#### Option A: Upload PDF/DOCX File

```bash
POST /api/vectors/collections/resume_database/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [your_resume.pdf]
```

#### Option B: Add Resume Text Directly

```bash
POST /api/vectors/collections/resume_database/documents
Authorization: Bearer {token}
{
  "text": "Your full resume content here..."
}
```

You can split your resume into sections:
- Education section
- Work Experience section
- Skills section
- Projects section
- Certifications section

This helps the search find more relevant matches!

---

### Step 2: Create Workflow

```bash
POST /api/workflows
Authorization: Bearer {token}
{
  "name": "Resume-Job Match Assistant",
  "description": "Matches resumes with job descriptions using vector search and AI analysis"
}
```

Save the `workflow_id`.

---

### Step 3: Create Vector Collection

The script will create `resume_database` collection automatically, or you can create it manually:

```bash
POST /api/vectors/collections
Authorization: Bearer {token}
{
  "name": "resume_database",
  "dimension": 384
}
```

---

### Step 4: Create Nodes

#### Node 1: FAISS Search - Find Relevant Resume Sections

```json
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Search Resume",
  "node_type": "faiss_search",
  "config": {
    "collection_name": "resume_database",
    "query": "{input.job_description}",
    "top_k": 5
  },
  "position_x": 100,
  "position_y": 200
}
```

**What it does:** Searches your resume for sections most relevant to the job description.

#### Node 2: LLM Call - Analyze Match Quality

```json
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Analyze Match",
  "node_type": "llm_call",
  "config": {
    "prompt_template": "You are a professional resume analyst. Analyze how well a candidate's resume matches a job description.\n\nJob Description:\n{input.job_description}\n\nRelevant Resume Sections:\n{input.Search Resume.results}\n\nProvide a comprehensive analysis:\n1. **Match Score**: Rate from 1-10 how well the resume matches the job\n2. **Key Strengths**: List top 3-5 matching qualifications, skills, or experiences\n3. **Relevant Experience**: Extract and highlight experience relevant to the job\n4. **Skills Match**: Identify matching technical skills, tools, and certifications\n5. **Gaps**: Mention any important requirements missing from the resume\n6. **Recommendations**: Suggest improvements to better align with the job\n\nFormat your response clearly with headers for each section.",
    "temperature": 0.7,
    "max_tokens": 800
  },
  "position_x": 400,
  "position_y": 200
}
```

**What it does:** Uses AI to analyze how well the resume matches the job and provides detailed insights.

#### Node 3: HTTP Request - Send Results (Optional)

```json
POST /api/workflows/{workflow_id}/nodes
{
  "name": "Send Results",
  "node_type": "http_request",
  "config": {
    "method": "POST",
    "url": "https://your-webhook-url.com/endpoint",
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
```

**What it does:** Sends the analysis results to an external service or webhook.

#### Node 4: DB Write - Save Match Analysis

```json
POST /api/workflows/{workflow_id}/nodes
{
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
```

**What it does:** Saves the match analysis to the database for future reference.

---

### Step 5: Connect Nodes

```bash
# Search Resume → Analyze Match
POST /api/workflows/{workflow_id}/edges
{
  "source_node_id": "{search_node_id}",
  "target_node_id": "{llm_node_id}"
}

# Analyze Match → Send Results
POST /api/workflows/{workflow_id}/edges
{
  "source_node_id": "{llm_node_id}",
  "target_node_id": "{http_node_id}"
}

# Analyze Match → Save Match Analysis
POST /api/workflows/{workflow_id}/edges
{
  "source_node_id": "{llm_node_id}",
  "target_node_id": "{db_node_id}"
}
```

---

## ▶️ Executing the Workflow

### Example 1: Software Engineer Position

```bash
POST /api/workflows/{workflow_id}/execute
Authorization: Bearer {token}
{
  "input_data": {
    "job_description": "We're looking for a Full-Stack Developer with 3+ years of experience. Required skills: React, TypeScript, Node.js, PostgreSQL, REST APIs. Experience with cloud deployment (AWS/Docker) is a plus."
  }
}
```

### Example 2: Data Scientist Position

```bash
POST /api/workflows/{workflow_id}/execute
{
  "input_data": {
    "job_description": "Data Scientist needed. Must have: Python, Machine Learning, SQL, Statistics, Data visualization. Experience with scikit-learn, pandas, and Jupyter notebooks required."
  }
}
```

### Example 3: DevOps Engineer Position

```bash
POST /api/workflows/{workflow_id}/execute
{
  "input_data": {
    "job_description": "DevOps Engineer position. Requirements: Docker, Kubernetes, AWS, CI/CD pipelines, Linux, Monitoring tools. Terraform experience preferred."
  }
}
```

---

## 📹 Video Demo Script

### Introduction (30 seconds)
"Today I'll demonstrate the AI Workflow Builder by creating a Resume-Job Match Assistant. This workflow analyzes how well a resume matches job descriptions using vector search and AI."

### Step 1: Show Resume Upload (20 seconds)
"First, I'll upload my resume to the vector database. The system will create embeddings that allow semantic search..."
[Show upload process]

### Step 2: Create Workflow (15 seconds)
"Now I'll create a workflow called 'Resume-Job Match Assistant'..."
[Create workflow]

### Step 3: Build Nodes (60 seconds)
"I'll add 4 nodes:
1. FAISS Search - finds relevant resume sections
2. LLM Analysis - matches and extracts insights
3. HTTP Request - sends results (optional)
4. DB Write - saves analysis"
[Create nodes visually]

### Step 4: Connect Nodes (20 seconds)
"Connect the nodes to define the data flow..."
[Connect nodes]

### Step 5: Execute with Real Job (45 seconds)
"Let's test it with a real job posting: 'Full-Stack Developer with React, Node.js, PostgreSQL...'"
[Execute workflow]

### Step 6: Show Results (45 seconds)
"The workflow:
- Found relevant sections from my resume
- Generated a match score and detailed analysis
- Highlighted my matching skills and experience
- Identified gaps and recommendations
- Saved everything to the database"
[Show results breakdown]

### Conclusion (15 seconds)
"This demonstrates how easy it is to build powerful AI workflows. Perfect for job seekers, recruiters, or anyone matching documents."

**Total: ~3.5 minutes**

---

## 🎯 Expected Output Example

When you execute the workflow, you'll get something like:

```json
{
  "run_id": "uuid",
  "status": "completed",
  "results": {
    "Search Resume": {
      "results": [
        "Experience: Full-Stack Developer at Tech Corp (2021-2024). Developed React applications...",
        "Skills: React, TypeScript, Node.js, PostgreSQL, REST APIs, Docker...",
        "Projects: Built e-commerce platform using React, Node.js, and PostgreSQL..."
      ]
    },
    "Analyze Match": {
      "output": "**Match Score**: 8.5/10\n\n**Key Strengths**:\n1. 4 years of Full-Stack experience (exceeds requirement)\n2. All required technologies match (React, Node.js, PostgreSQL)\n3. REST API experience demonstrated in projects\n\n**Relevant Experience**:\n- Built scalable web applications using React and Node.js\n- Database design and optimization with PostgreSQL\n- API development and integration\n\n**Skills Match**:\n✅ React ✅ TypeScript ✅ Node.js ✅ PostgreSQL ✅ REST APIs ✅ Docker\n\n**Gaps**:\n- Limited AWS experience mentioned\n\n**Recommendations**:\n- Highlight any cloud deployment experience\n- Add specific metrics from projects"
    }
  }
}
```

---

## ✅ Checklist for Video

- [ ] Resume uploaded to vector database
- [ ] Workflow created with all 4 node types
- [ ] All nodes connected properly
- [ ] Test execution with sample job description
- [ ] Results reviewed and make sense
- [ ] Screenshots/recordings ready
- [ ] Clear explanation script prepared

---

## 💡 Tips for Best Results

1. **Upload Complete Resume**: Include all sections (experience, skills, education, projects)
2. **Split into Sections**: Upload different sections separately for better search results
3. **Use Clear Job Descriptions**: More detailed job descriptions yield better analysis
4. **Review LLM Output**: The AI analysis is comprehensive but always review for accuracy
5. **Iterate**: Try different job descriptions to see how match scores vary

---

## 🔄 Workflow Variations

### Simple Version (2 Nodes)
- FAISS Search → LLM Analysis
- Removes HTTP and DB nodes for simplicity

### Advanced Version (5+ Nodes)
- Add multiple LLM nodes for different analyses
- Add conditional logic (future feature)
- Add email notification node

---

Good luck with your video! 🎥✨

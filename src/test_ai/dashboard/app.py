"""Streamlit dashboard for AI Workflow Orchestrator."""
import json
import streamlit as st
from datetime import datetime

from test_ai.orchestrator import WorkflowEngine, Workflow, WorkflowStep, StepType
from test_ai.prompts import PromptTemplateManager, PromptTemplate
from test_ai.api_clients import OpenAIClient, GitHubClient, NotionClientWrapper


# Initialize components
@st.cache_resource
def get_workflow_engine():
    """Get cached workflow engine."""
    return WorkflowEngine()


@st.cache_resource
def get_prompt_manager():
    """Get cached prompt manager."""
    return PromptTemplateManager()


@st.cache_resource
def get_openai_client():
    """Get cached OpenAI client."""
    return OpenAIClient()


def render_sidebar():
    """Render sidebar navigation."""
    st.sidebar.title("🤖 AI Workflow Orchestrator")
    
    pages = {
        "Dashboard": "📊",
        "Workflows": "⚙️",
        "Prompts": "📝",
        "Execute": "▶️",
        "Logs": "📋"
    }
    
    page = st.sidebar.radio(
        "Navigation",
        list(pages.keys()),
        format_func=lambda x: f"{pages[x]} {x}"
    )
    
    return page


def render_dashboard_page():
    """Render main dashboard page."""
    st.title("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    workflow_engine = get_workflow_engine()
    prompt_manager = get_prompt_manager()
    
    workflows = workflow_engine.list_workflows()
    prompts = prompt_manager.list_templates()
    
    with col1:
        st.metric("Workflows", len(workflows))
    
    with col2:
        st.metric("Prompt Templates", len(prompts))
    
    with col3:
        st.metric("Status", "Active", delta="Running")
    
    st.divider()
    
    st.subheader("Recent Activity")
    st.info("No recent activity")
    
    st.divider()
    
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🆕 Create Workflow", use_container_width=True):
            st.session_state.page = "Workflows"
            st.rerun()
    
    with col2:
        if st.button("📝 Create Prompt", use_container_width=True):
            st.session_state.page = "Prompts"
            st.rerun()


def render_workflows_page():
    """Render workflows management page."""
    st.title("⚙️ Workflows")
    
    workflow_engine = get_workflow_engine()
    
    tab1, tab2 = st.tabs(["📋 List Workflows", "➕ Create Workflow"])
    
    with tab1:
        workflows = workflow_engine.list_workflows()
        
        if workflows:
            for wf in workflows:
                with st.expander(f"**{wf['name']}** - {wf['id']}"):
                    st.write(wf['description'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Details", key=f"view_{wf['id']}"):
                            workflow = workflow_engine.load_workflow(wf['id'])
                            st.json(workflow.model_dump())
                    with col2:
                        if st.button("Execute", key=f"exec_{wf['id']}"):
                            st.session_state.execute_workflow_id = wf['id']
                            st.session_state.page = "Execute"
                            st.rerun()
        else:
            st.info("No workflows found. Create your first workflow!")
    
    with tab2:
        st.subheader("Create New Workflow")
        
        wf_id = st.text_input("Workflow ID", placeholder="my_workflow")
        wf_name = st.text_input("Workflow Name", placeholder="My Workflow")
        wf_description = st.text_area("Description", placeholder="Describe what this workflow does")
        
        st.subheader("Steps")
        
        num_steps = st.number_input("Number of Steps", min_value=1, max_value=10, value=1)
        
        steps = []
        for i in range(num_steps):
            st.markdown(f"**Step {i+1}**")
            
            col1, col2 = st.columns(2)
            with col1:
                step_id = st.text_input(f"Step ID", key=f"step_id_{i}", value=f"step_{i+1}")
                step_type = st.selectbox(
                    "Step Type",
                    [st.value for st in StepType],
                    key=f"step_type_{i}"
                )
            with col2:
                step_action = st.text_input("Action", key=f"step_action_{i}")
                next_step = st.text_input("Next Step ID (optional)", key=f"next_step_{i}")
            
            params_json = st.text_area(
                "Parameters (JSON)",
                value="{}",
                key=f"step_params_{i}",
                height=100
            )
            
            try:
                params = json.loads(params_json)
                steps.append(WorkflowStep(
                    id=step_id,
                    type=step_type,
                    action=step_action,
                    params=params,
                    next_step=next_step if next_step else None
                ))
            except json.JSONDecodeError:
                st.error(f"Invalid JSON in Step {i+1} parameters")
            
            st.divider()
        
        if st.button("💾 Save Workflow", type="primary"):
            if wf_id and wf_name:
                workflow = Workflow(
                    id=wf_id,
                    name=wf_name,
                    description=wf_description,
                    steps=steps
                )
                
                if workflow_engine.save_workflow(workflow):
                    st.success(f"Workflow '{wf_name}' saved successfully!")
                    st.balloons()
                else:
                    st.error("Failed to save workflow")
            else:
                st.warning("Please fill in Workflow ID and Name")


def render_prompts_page():
    """Render prompts management page."""
    st.title("📝 Prompt Templates")
    
    prompt_manager = get_prompt_manager()
    
    tab1, tab2 = st.tabs(["📋 List Templates", "➕ Create Template"])
    
    with tab1:
        prompts = prompt_manager.list_templates()
        
        if prompts:
            for prompt in prompts:
                with st.expander(f"**{prompt['name']}** - {prompt['id']}"):
                    st.write(prompt['description'])
                    
                    template = prompt_manager.load_template(prompt['id'])
                    if template:
                        st.code(template.user_prompt, language="text")
                        
                        if st.button("Delete", key=f"del_{prompt['id']}"):
                            if prompt_manager.delete_template(prompt['id']):
                                st.success("Template deleted!")
                                st.rerun()
        else:
            st.info("No templates found. Create your first template!")
            
            if st.button("Create Default Templates"):
                prompt_manager.create_default_templates()
                st.success("Default templates created!")
                st.rerun()
    
    with tab2:
        st.subheader("Create New Template")
        
        template_id = st.text_input("Template ID", placeholder="my_template")
        template_name = st.text_input("Template Name", placeholder="My Template")
        template_description = st.text_area("Description", placeholder="Describe this template")
        
        system_prompt = st.text_area(
            "System Prompt (optional)",
            placeholder="You are a helpful assistant..."
        )
        
        user_prompt = st.text_area(
            "User Prompt",
            placeholder="Enter your prompt template here. Use {variable_name} for variables.",
            height=200
        )
        
        variables = st.text_input(
            "Variables (comma-separated)",
            placeholder="email_content, task_description"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
        with col2:
            temperature = st.slider("Temperature", 0.0, 2.0, 0.7)
        
        if st.button("💾 Save Template", type="primary"):
            if template_id and template_name and user_prompt:
                template = PromptTemplate(
                    id=template_id,
                    name=template_name,
                    description=template_description,
                    system_prompt=system_prompt if system_prompt else None,
                    user_prompt=user_prompt,
                    variables=[v.strip() for v in variables.split(",")] if variables else [],
                    model=model,
                    temperature=temperature
                )
                
                if prompt_manager.save_template(template):
                    st.success(f"Template '{template_name}' saved successfully!")
                    st.balloons()
                else:
                    st.error("Failed to save template")
            else:
                st.warning("Please fill in Template ID, Name, and User Prompt")


def render_execute_page():
    """Render workflow execution page."""
    st.title("▶️ Execute Workflow")
    
    workflow_engine = get_workflow_engine()
    workflows = workflow_engine.list_workflows()
    
    if not workflows:
        st.warning("No workflows available. Create a workflow first!")
        return
    
    workflow_options = {wf['id']: wf['name'] for wf in workflows}
    
    selected_id = st.selectbox(
        "Select Workflow",
        options=list(workflow_options.keys()),
        format_func=lambda x: workflow_options[x]
    )
    
    if selected_id:
        workflow = workflow_engine.load_workflow(selected_id)
        
        if workflow:
            st.info(workflow.description)
            
            st.subheader("Workflow Variables")
            
            variables = {}
            if workflow.variables:
                for key, value in workflow.variables.items():
                    variables[key] = st.text_input(f"{key}", value=str(value))
            
            additional_vars = st.text_area(
                "Additional Variables (JSON)",
                value="{}",
                help="Add extra variables as JSON"
            )
            
            if st.button("🚀 Execute Workflow", type="primary"):
                with st.spinner("Executing workflow..."):
                    try:
                        if additional_vars:
                            extra = json.loads(additional_vars)
                            variables.update(extra)
                        
                        workflow.variables = variables
                        result = workflow_engine.execute_workflow(workflow)
                        
                        st.success(f"Workflow completed with status: {result.status}")
                        
                        st.subheader("Execution Results")
                        st.json(result.model_dump(mode='json'))
                        
                    except Exception as e:
                        st.error(f"Error executing workflow: {str(e)}")


def render_logs_page():
    """Render logs page."""
    st.title("📋 Workflow Logs")
    
    workflow_engine = get_workflow_engine()
    logs_dir = workflow_engine.settings.logs_dir
    
    log_files = sorted(logs_dir.glob("workflow_*.json"), reverse=True)
    
    if log_files:
        for log_file in log_files[:20]:
            with st.expander(f"📄 {log_file.name}"):
                try:
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)
                    
                    st.json(log_data)
                except Exception as e:
                    st.error(f"Error loading log: {str(e)}")
    else:
        st.info("No logs found. Execute a workflow to generate logs.")


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="AI Workflow Orchestrator",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'Dashboard'
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Update session state if changed via sidebar
    st.session_state.page = page
    
    # Render the selected page
    if page == "Dashboard":
        render_dashboard_page()
    elif page == "Workflows":
        render_workflows_page()
    elif page == "Prompts":
        render_prompts_page()
    elif page == "Execute":
        render_execute_page()
    elif page == "Logs":
        render_logs_page()


def run_dashboard():
    """Run the Streamlit dashboard."""
    main()


if __name__ == "__main__":
    main()

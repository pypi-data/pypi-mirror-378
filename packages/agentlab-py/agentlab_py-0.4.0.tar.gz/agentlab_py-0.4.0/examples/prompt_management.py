#!/usr/bin/env python3
"""
Example: AgentLab Prompt Management

This example demonstrates how to:
- Define a prompt with version
- Try to fetch the prompt version
- Create prompts if they don't exist (404)
- Fetch and cache prompts from AgentLab
- Display the final prompt

Setup:
1. Set your API token as an environment variable:
   export AGENTLAB_API_TOKEN=your-api-token-here
   
2. Or pass it directly to AgentLabClientOptions
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path to import agentlab
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from agentlab import AgentLabClient, CreateAgentVersionOptions

# Define our prompt and version at the start
AGENT_NAME = "example-assistant"
PROMPT_VERSION = "v1.2.0"
PROMPTS = {
    "system": """You are an advanced AI assistant specialized in providing detailed, accurate, and helpful responses. 
Always be polite, professional, and aim to understand the user's context before responding. 
When uncertain, ask clarifying questions. Remember to be concise yet thorough in your explanations.""",
    
    "user_greeting": "Hello! I'm your AI assistant. How can I assist you today? Feel free to ask me anything - I'm here to help! 🤖",
    
    "error_response": """I apologize, but I encountered an error while processing your request. 
Please try again or contact support if the issue persists. If the problem continues, please provide more details about what you were trying to do so I can better assist you.""",

    "context_request": "Could you provide more context about your request? Additional details will help me give you a more accurate and helpful response tailored to your needs.",

    "farewell": "Thank you for using our AI assistant! If you have any more questions in the future, don't hesitate to ask. Have a wonderful day! 👋",

    "thinking_prompt": "Let me think about this step by step to provide you with the best possible answer."
}

# Metadata for the prompt version
METADATA = {
    "author": "AgentLab Team",
    "purpose": "Enhanced assistant prompts with context awareness and personality", 
    "version_notes": "v1.2.0: Added emojis to greetings/farewell, improved context request clarity, added new thinking_prompt, enhanced system prompt with conciseness note",
    "created_at": datetime.now().isoformat()
}

# Cache for prompts
cached_prompts = None


def main():
    """Main function demonstrating prompt management flow."""
    global cached_prompts
    
    try:
        # Initialize the AgentLab client
        print("🚀 Initializing AgentLab client...")
        client = AgentLabClient()
        
        print(f"📝 Working with agent: {AGENT_NAME}, version: {PROMPT_VERSION}")
        
        # Step 1: Try to fetch the existing prompt version
        print("\n🔍 Attempting to fetch existing prompts...")
        
        try:
            existing_prompts = client.get_agent_version(AGENT_NAME, PROMPT_VERSION)
            print("✅ Found existing prompts in AgentLab!")
            print(f"   Content hash: {existing_prompts.content_hash}")
            create_time_str = existing_prompts.create_time.strftime('%Y-%m-%d %H:%M:%S') if existing_prompts.create_time else 'Unknown'
            print(f"   Created: {create_time_str}")
            
            # Cache the prompts
            cached_prompts = existing_prompts
            
        except Exception as error:
            # Check if it's a 404 (Not Found) error
            if "404" in str(error) or "NOT_FOUND" in str(error.upper()) or "not found" in str(error).lower():
                print("❌ Prompts not found (404). Creating new version...")
                
                # Step 2: Create the prompts since they don't exist
                print("\n📤 Creating prompts in AgentLab...")
                
                create_options = CreateAgentVersionOptions(
                    agent_name=AGENT_NAME,
                    version=PROMPT_VERSION,
                    prompts=PROMPTS,
                    metadata=METADATA,
                    description="Enhanced example assistant with improved contextual prompts"
                )
                
                created_prompts = client.create_agent_version(create_options)
                
                print("✅ Successfully created prompts!")
                print(f"   Resource name: {created_prompts.name}")
                print(f"   Content hash: {created_prompts.content_hash}")
                print(f"   Created by: {created_prompts.created_by}")
                
                # Cache the created prompts
                cached_prompts = created_prompts
                
            else:
                # Re-raise if it's a different error
                raise error
        
        # Step 3: Display the cached prompts
        print("\n📋 Current prompts:")
        print("=" * 50)
        
        if cached_prompts and cached_prompts.prompts:
            for prompt_name, prompt_content in cached_prompts.prompts.items():
                print(f"\n{prompt_name.upper()}:")
                print("-" * 20)
                print(prompt_content)
        
        # Step 4: Show metadata if available
        if cached_prompts and cached_prompts.metadata:
            print("\n🏷️  Metadata:")
            print("-" * 20)
            for key, value in cached_prompts.metadata.items():
                print(f"{key}: {value}")
        
        # Step 5: List all versions for this agent to show versioning capability
        print("\n📚 All versions for this agent:")
        print("-" * 30)
        
        try:
            all_versions = client.list_agent_versions(AGENT_NAME)
            
            if all_versions.agent_versions:
                for index, version in enumerate(all_versions.agent_versions):
                    print(f"{index + 1}. Version: {version.version}")
                    create_time_str = version.create_time.strftime('%Y-%m-%d %H:%M:%S') if version.create_time else 'Unknown'
                    print(f"   Created: {create_time_str}")
                    print(f"   Hash: {version.content_hash}")
                    print(f"   Prompt count: {len(version.prompts)}")
                    print("")
            else:
                print("No versions found.")
                
        except Exception as error:
            print(f"Error listing versions: {error}")
        
        print("\n🎉 Prompt management flow completed successfully!")
        
        # Step 6: Show the beautiful string representation
        print("\n" + "=" * 60)
        print("CACHED PROMPTS (Pretty Print):")
        print("=" * 60)
        print(cached_prompts)
        
    except Exception as error:
        print("❌ Error in prompt management flow:")
        print(f"   Message: {error}")
        print(f"   Type: {type(error).__name__}")
        
        # Show more details for debugging
        import traceback
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        
        sys.exit(1)


# Helper function for consistent formatting
def format_separator(char="=", length=50):
    """Create a separator line."""
    return char * length


# Run the example
if __name__ == "__main__":
    print('🐍 AgentLab Python Client - Prompt Management Example')
    print(format_separator())
    
    main()
    
    print('\n📚 Next steps:')
    print('  - Set your API token: export AGENTLAB_API_TOKEN=your-token-here')
    print('  - The project ID is auto-detected from your auth context')
    print('  - Try modifying the prompts and creating new versions')
    print('  - Explore version diff capabilities with different prompt versions')
    print('  - Use the pythonic models for easier integration in your applications')

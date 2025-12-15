# Quick Start Guide: AI Workflow from Notion

This guide will help you set up and run AI workflows from Notion in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- Notion account
- OpenAI account

## Step 1: Create Notion Database (2 min)

1. Open Notion and create a new database (Table view)
2. Add these properties:

| Property Name   | Property Type | Required |
|----------------|---------------|----------|
| Name           | Title         | ✓        |
| Status         | Select        | ✓        |
| Prompt         | Text          | ✓        |
| System Message | Text          |          |
| Temperature    | Number        |          |
| Max Tokens     | Number        |          |
| Result         | Text          |          |
| Last Executed  | Date          |          |

3. For the **Status** property, add these options:
   - Active
   - Running
   - Completed
   - Failed

4. Add a sample workflow:
   - **Name**: "Test Workflow"
   - **Status**: "Active"
   - **Prompt**: "Write a haiku about automation"

## Step 2: Get API Keys (2 min)

### Notion API Key:
1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it (e.g., "AI Workflow")
4. Copy the "Internal Integration Token"
5. Share your database with this integration:
   - Open your database in Notion
   - Click "..." menu → "Add connections" → Select your integration

### Notion Database ID:
- From your database URL: `https://notion.so/[workspace]/[DATABASE_ID]?v=...`
- Copy the 32-character `DATABASE_ID`

### OpenAI API Key:
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy it immediately (won't be shown again)

## Step 3: Configure (1 min)

```bash
cd ai_workflow/config
cp config.env.example config.env
```

Edit `config.env`:
```env
NOTION_API_KEY=secret_abc123...
NOTION_DATABASE_ID=abc123def456...
OPENAI_API_KEY=sk-abc123...
AI_MODEL=gpt-3.5-turbo
WORKFLOW_STATUS_FILTER=Active
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Run!

Test the setup:
```bash
cd ai_workflow
python examples/test_notion_client.py
python examples/test_ai_executor.py
```

Run workflows:
```bash
python examples/run_workflows.py
```

## What Happens?

1. ✓ Fetches all "Active" workflows from your Notion database
2. ✓ Updates status to "Running"
3. ✓ Sends the prompt to OpenAI
4. ✓ Updates status to "Completed" with the result
5. ✓ Records execution time in "Last Executed"

Check your Notion database to see the results!

## Common Issues

**"NOTION_API_KEY not found"**
- Make sure `config.env` exists in `ai_workflow/config/`
- Check that you copied the file correctly

**"Database not found"**
- Ensure you shared the database with your Notion integration
- Verify the DATABASE_ID is correct (32 characters)

**"OpenAI API error"**
- Check your OpenAI account has credits
- Verify the API key is valid

## Next Steps

- Add more workflows in Notion
- Set up GitHub Actions for automation (see main README)
- Customize prompts for your use case
- Integrate with your SaaS application

For full documentation, see [ai_workflow/README.md](ai_workflow/README.md)

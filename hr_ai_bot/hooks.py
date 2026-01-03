def post_init_hook(env):
    # Create pgvector extension and embedding table
    env.cr.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Create embedding table if not exists
    env.cr.execute("""
        CREATE TABLE IF NOT EXISTS hr_ai_embedding (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding vector(768) NOT NULL,
            create_date TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Create index for vector similarity search
    env.cr.execute("""
        CREATE INDEX IF NOT EXISTS hr_ai_embedding_vector_idx 
        ON hr_ai_embedding USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)
    
    # On some stacks discuss may not be installed; guard to avoid install failure
    if 'discuss.channel' not in env:
        return

    Channel = env['discuss.channel']

    channel = Channel.search([('name', '=', 'HR AI Assistant')], limit=1)
    if not channel:
        Channel.create({
            'name': 'HR AI Assistant',
            'channel_type': 'channel',
        })

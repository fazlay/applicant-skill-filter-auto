def post_init_hook(env):
    env.cr.execute("CREATE EXTENSION IF NOT EXISTS vector")

    env.cr.execute("""
        CREATE TABLE IF NOT EXISTS hr_ai_embedding (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding vector NOT NULL,
            create_date TIMESTAMP DEFAULT NOW()
        )
    """)

    env.cr.execute("""
        CREATE INDEX IF NOT EXISTS hr_ai_embedding_vector_idx
        ON hr_ai_embedding USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    Partner = env['res.partner']
    bot_partner = Partner.search([('name', '=', 'HR AI Assistant Bot')], limit=1)
    if not bot_partner:
        bot_partner = Partner.create({
            'name': 'HR AI Assistant Bot',
            'email': 'hr.ai.bot@company.com',
            'active': True,
            'is_company': False,
        })

    ICP = env['ir.config_parameter'].sudo()
    ICP.set_param('hr_ai_bot.bot_partner_id', str(bot_partner.id))

    if 'discuss.channel' not in env:
        return

    Channel = env['discuss.channel']
    channel = Channel.search([('name', '=', 'HR AI Assistant')], limit=1)
    if not channel:
        Channel.create({
            'name': 'HR AI Assistant',
            'channel_type': 'channel',
        })

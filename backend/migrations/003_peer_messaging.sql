-- Direct user-to-user threads and messages

CREATE TABLE IF NOT EXISTS peer_threads (
    id UUID PRIMARY KEY,
    user_a_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_b_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    last_message_at TIMESTAMPTZ,
    last_message_preview VARCHAR(300),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_peer_threads_pair UNIQUE (user_a_id, user_b_id)
);

CREATE INDEX IF NOT EXISTS ix_peer_threads_user_a ON peer_threads(user_a_id);
CREATE INDEX IF NOT EXISTS ix_peer_threads_user_b ON peer_threads(user_b_id);

CREATE TABLE IF NOT EXISTS peer_messages (
    id UUID PRIMARY KEY,
    thread_id UUID NOT NULL REFERENCES peer_threads(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_peer_messages_thread_id ON peer_messages(thread_id);
CREATE INDEX IF NOT EXISTS ix_peer_messages_created_at ON peer_messages(created_at);

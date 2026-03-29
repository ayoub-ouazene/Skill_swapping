-- Skills the user wants to learn (profile)
CREATE TABLE IF NOT EXISTS desired_skills (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    CONSTRAINT uq_desired_skills_user_name UNIQUE (user_id, skill_name)
);

CREATE INDEX IF NOT EXISTS ix_desired_skills_user_id ON desired_skills(user_id);

-- ============================================================
-- PhoneBook Stored Procedures & Functions  (TSIS 1)
-- Requires schema.sql to have been applied first.
-- ============================================================

-- ------------------------------------------------------------
-- 1. add_phone
--    Adds a phone number to an existing contact (by username).
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Resolve the contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE username = p_contact_name
       OR name     = p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Validate type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Must be home, work, or mobile.', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact %.', p_phone, p_type, p_contact_name;
END;
$$;


-- ------------------------------------------------------------
-- 2. move_to_group
--    Moves a contact to a group; creates the group if needed.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Resolve contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE username = p_contact_name
       OR name     = p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Get or create group
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        RAISE NOTICE 'Created new group "%".', p_group_name;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- ------------------------------------------------------------
-- 3. search_contacts  (extends Practice 8 pattern-search)
--    Matches against: name, username, email, AND all phones.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    name       VARCHAR,
    username   VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql AS $$
DECLARE
    v_pattern TEXT := '%' || p_query || '%';
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.username,
        c.email,
        c.birthday,
        g.name           AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', '
                   ORDER BY p.id) AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.name     ILIKE v_pattern OR
        c.username ILIKE v_pattern OR
        c.email    ILIKE v_pattern OR
        EXISTS (
            SELECT 1 FROM phones ph
            WHERE ph.contact_id = c.id
              AND ph.phone ILIKE v_pattern
        )
    GROUP BY c.id, c.name, c.username, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.name;
END;
$$;


-- ------------------------------------------------------------
-- 4. get_contacts_page  (paginated listing – re-declared here
--    so the file is self-contained; safe to run over Practice 8)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_contacts_page(
    p_limit  INTEGER,
    p_offset INTEGER
)
RETURNS TABLE (
    id         INTEGER,
    name       VARCHAR,
    username   VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.username,
        c.email,
        c.birthday,
        g.name AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', '
                   ORDER BY p.id) AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    GROUP BY c.id, c.name, c.username, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.name
    LIMIT p_limit OFFSET p_offset;
END;
$$;
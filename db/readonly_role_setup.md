# Create the database read-only role

Run these commands as your PostgreSQL administrator. They do not store a
password in the repository.

```powershell
psql -U postgres -h localhost -d text_to_sql_learning -f db/create_readonly_role.sql
psql -U postgres -h localhost -d text_to_sql_learning
```

At the `psql` prompt, set the role password interactively:

```sql
\password text_to_sql_reader
\q
```

Test that it can read:

```powershell
psql -U text_to_sql_reader -h localhost -d text_to_sql_learning -c "SELECT count(*) FROM customers;"
```

Do not use this role to run schema migrations. It is intended for generated
read-only queries.

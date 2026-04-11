# 🗄️ Database Configuration Guide

## Quick Summary

| Environment | Database | Config |
|------------|----------|--------|
| **Local Development** | SQLite (default) | Leave DB_* empty |
| **Render Production** | PostgreSQL | Auto-configured |
| **Alternative** | MySQL or PostgreSQL | Manual setup |

---

## 1️⃣ LOCAL DEVELOPMENT (Recommended)

### SQLite (Default - Easiest)
- No setup required
- Perfect for development
- File: `db.sqlite3`

**Usage:**
```bash
# Leave all DB_* variables empty in .env (or comment them out)
DB_ENGINE=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Then run normally
python manage.py migrate
python manage.py runserver
```

✅ **Best for**: Learning, testing, small teams, quick development

---

## 2️⃣ RENDER PRODUCTION (Recommended)

### PostgreSQL (Auto-Configured)
- Render automatically creates PostgreSQL database
- Credentials auto-injected via environment variables
- Included in `render.yaml`

**Configuration:**
```yaml
databases:
  - name: home-rental-db
    databaseName: home_rental_db
    user: home_rental_user
    plan: free
    version: 15
```

**Environment Variables (Set by Render):**
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=home_rental_db
DB_USER=home_rental_user
DB_PASSWORD=[auto-generated]
DB_HOST=[render-provided-host]
DB_PORT=5432
```

✅ **Why PostgreSQL on Render?**
- More reliable than SQLite for production
- Better performance
- Supports concurrent users
- Free tier included
- Automatic backups

---

## 3️⃣ LOCAL WITH PostgreSQL (Optional)

For testing Render-like environment locally:

### Windows Installation

1. **Install PostgreSQL:**
   ```bash
   # Using Chocolatey
   choco install postgresql
   
   # Or download from: https://www.postgresql.org/download/windows/
   ```

2. **Create Database:**
   ```bash
   # In PowerShell (as admin)
   psql -U postgres
   
   # Then in psql:
   CREATE DATABASE home_rental_db;
   CREATE USER home_rental_user WITH PASSWORD 'your-password';
   ALTER ROLE home_rental_user SET client_encoding TO 'utf8';
   ALTER ROLE home_rental_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE home_rental_user SET default_transaction_deferrable TO on;
   GRANT ALL PRIVILEGES ON DATABASE home_rental_db TO home_rental_user;
   \q
   ```

3. **Update .env:**
   ```
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=home_rental_db
   DB_USER=home_rental_user
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Run:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

✅ **Why?** Test production database locally before deploying

---

## 4️⃣ ALTERNATIVE: MySQL

If you prefer MySQL:

### Windows Installation

1. **Install MySQL:**
   ```bash
   # Using Chocolatey
   choco install mysql
   
   # Or download from: https://dev.mysql.com/downloads/mysql/
   ```

2. **Create Database:**
   ```bash
   mysql -u root
   
   # In MySQL:
   CREATE DATABASE home_rental;
   CREATE USER 'home_rental_user'@'localhost' IDENTIFIED BY 'your-password';
   GRANT ALL PRIVILEGES ON home_rental.* TO 'home_rental_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

3. **Update .env:**
   ```
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=home_rental
   DB_USER=home_rental_user
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=3306
   ```

4. **Run:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

✅ **Already in requirements.txt**: `mysqlclient==2.2.8`

---

## Database Selection Guide

### Choose SQLite if:
- ✅ Solo development
- ✅ Learning Django
- ✅ Small project
- ✅ No production yet
- ✅ Want zero setup

### Choose PostgreSQL if:
- ✅ Production deployment on Render (Recommended!)
- ✅ Multiple concurrent users
- ✅ Complex queries
- ✅ Want to test production locally
- ✅ Better performance needed

### Choose MySQL if:
- ✅ Already using MySQL elsewhere
- ✅ Team standardizes MySQL
- ✅ Hosting requires MySQL
- ✅ Migrating from existing MySQL app

---

## Django Settings.py Logic

The application automatically chooses the database:

```python
# Priority (in order):
1. PostgreSQL if DB_ENGINE contains "postgresql"
2. MySQL if DB_ENGINE contains "mysql"
3. SQLite (Default) if DB_* variables are empty
```

**Example Scenarios:**

```python
# Scenario 1: Development (empty DB vars)
# Result: SQLite used
DB_ENGINE=
DB_NAME=
DB_HOST=

# Scenario 2: PostgreSQL Production (Render)
# Result: PostgreSQL used
DB_ENGINE=django.db.backends.postgresql
DB_NAME=home_rental_db
DB_HOST=db.render.example.com

# Scenario 3: MySQL
# Result: MySQL used
DB_ENGINE=django.db.backends.mysql
DB_NAME=home_rental
DB_HOST=localhost
```

---

## Switching Databases

### From SQLite → PostgreSQL:

1. **Export data (if you have production data):**
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Update .env** with PostgreSQL credentials

3. **Run migrations** on new database:
   ```bash
   python manage.py migrate
   python manage.py migrate --run-syncdb  # If needed
   ```

4. **Load data (if applicable):**
   ```bash
   python manage.py loaddata data.json
   ```

### From MySQL → PostgreSQL:

```bash
# Export from MySQL
python manage.py dumpdata > data.json

# Update .env to PostgreSQL
DB_ENGINE=django.db.backends.postgresql
# ... (set other PostgreSQL vars)

# Migrate
python manage.py migrate

# Load data
python manage.py loaddata data.json
```

---

## Production Deployment on Render

✅ **PostgreSQL is auto-configured!**

1. Push your code to GitHub
2. Deploy on Render using `render.yaml`
3. Render automatically:
   - Creates PostgreSQL database
   - Generates secure credentials
   - Injects environment variables
   - Runs migrations during build

**No manual database setup needed!**

---

## Connection Strings

For reference only (auto-handled by Django):

### SQLite
```
sqlite:///db.sqlite3
```

### PostgreSQL
```
postgresql://home_rental_user:password@localhost:5432/home_rental_db
```

### MySQL
```
mysql://home_rental_user:password@localhost:3306/home_rental
```

---

## Troubleshooting

### "No database connection"
```bash
# Check DB_ENGINE is set correctly
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES)
```

### "Relations do not exist"
```bash
# Run migrations
python manage.py migrate
```

### "Password authentication failed"
- Check DB_PASSWORD is correct
- PostgreSQL: Ensure user has CREATE privileges
- MySQL: Check user@host permissions

---

## Current Setup for Your Project

✅ **Local Development**: SQLite (db.sqlite3)
✅ **Render Production**: PostgreSQL (auto-configured)
✅ **Fallback Support**: MySQL still supported

Everything is configured! Just:
1. Leave DB_* empty for local dev (SQLite)
2. Deploy to Render (PostgreSQL auto-setup)
3. Enjoy! 🚀

---

## Next Steps

1. **For Local Development:**
   ```bash
   # Keep .env DB vars empty
   python manage.py migrate
   python manage.py runserver
   ```

2. **For Render Deployment:**
   ```bash
   git push origin main
   # Render handles everything!
   ```

3. **Optional - Test PostgreSQL Locally:**
   - Follow "Local with PostgreSQL" section above
   - Ensures compatibility before production

That's it! Your database is fully configured. ✅

# Vercel Environment Variables Setup

## Your Neon DB Connection String

Use this exact connection string in Vercel's `DATABASE_URL` environment variable:

```
postgresql://neondb_owner:npg_dyFJ5zZ0fWPj@ep-green-glade-a4x5w9dj-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

## Complete Vercel Environment Variables

Add these three environment variables in your Vercel project:

| Variable Name | Value |
|--------------|-------|
| **SECRET_KEY** | `your-random-secret-key` (or generate a new one) |
| **GOOGLE_AI_API_KEY** | `UPxvPmawZHRJf2KD6GAGvhY8uVkTh-u4` |
| **DATABASE_URL** | `postgresql://neondb_owner:npg_dyFJ5zZ0fWPj@ep-green-glade-a4x5w9dj-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require` |

## Steps to Set in Vercel

1. Go to your Vercel project
2. Navigate to **Settings** → **Environment Variables**
3. For each variable:
   - Click **"Add"** or edit existing
   - Enter the **Key** name
   - Paste the **Value**
   - Select environments: **Production**, **Preview**, **Development**
   - Click **Save**

## Generate a Secure SECRET_KEY

If you need to generate a new SECRET_KEY:

```python
import secrets
print(secrets.token_hex(32))
```

Or use online tool: https://randomkeygen.com/

## Important Notes

- ✅ Use `postgresql://` (not `postgres://`) in DATABASE_URL
- ✅ Keep the `?sslmode=require&channel_binding=require` part
- ✅ After adding variables, **redeploy** your project for changes to take effect
- ✅ Never commit these values to GitHub (they're already in .gitignore)

## After Setting Variables

1. **Redeploy** your project in Vercel
2. Visit: `https://your-project.vercel.app/init-db` to initialize tables
3. Test your app!

---

**Your Neon Connection String:**
```
postgresql://neondb_owner:npg_dyFJ5zZ0fWPj@ep-green-glade-a4x5w9dj-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```



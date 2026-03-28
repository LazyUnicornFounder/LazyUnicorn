# Lazy Auth

> Category: 🛠️ Dev · Version: 0.0.3

## Prompt

````
[Lazy Auth Prompt — v0.0.1 — LazyUnicorn.ai]

Add a complete authentication system called Lazy Auth to this project. It installs Google Sign-In, email/password login, protected routes, user profiles, role-based access control, and a user management dashboard — in one prompt. Uses Lovable Cloud and Supabase Auth.

Note: Google authentication requires Lovable Cloud to be enabled. Go to Cloud → Users → Auth → Google to enable Sign in with Google after this prompt runs.

---

1. Database

Create these Supabase tables with RLS enabled:

auth_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), google_auth_enabled (boolean, default true), email_auth_enabled (boolean, default true), magic_link_enabled (boolean, default false), default_role (text, default 'user'), redirect_after_login (text, default '/dashboard'), redirect_after_logout (text, default '/'), is_running (boolean, default false), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

user_profiles: id (uuid, primary key references auth.users on delete cascade), email (text), full_name (text), avatar_url (text), role (text, default 'user' — one of user, admin, moderator), onboarded (boolean, default false), last_seen (timestamptz), created_at (timestamptz, default now())

auth_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

Row Level Security policies:
- user_profiles: users can read and update their own row. Admins can read all rows.
- auth_settings: only admins can read and update.

Create a Supabase database trigger: when a new row is inserted into auth.users automatically insert a matching row into user_profiles with the user's email, full_name from raw_user_meta_data, and avatar_url from raw_user_meta_data. This ensures every user has a profile row immediately after signup.

---

2. Setup page

Create a page at /lazy-auth-setup.

Welcome message: 'Add Google Sign-In, protected routes, and user management to your Lovable site in one prompt. Lazy Auth handles signup, login, sessions, and access control automatically.'

Form fields:
- Brand name (text)
- Site URL (text)
- Enable Google Sign-In (toggle, default on) — note shown below: After setup go to Cloud → Users → Auth → Google in Lovable and enable Sign in with Google. Lovable manages the OAuth credentials for you — no Google Cloud configuration required unless you need custom branding.
- Enable email/password login (toggle, default on)
- Enable magic link login (toggle, default off) — users sign in with a link sent to their email, no password required
- Default user role (select: user / member / viewer) — the role assigned to all new signups
- Redirect after login (text, default /dashboard) — where users go after signing in
- Redirect after logout (text, default /) — where users go after signing out
- Protected routes (text, comma separated, e.g. /dashboard, /account, /settings) — routes that require authentication. Unauthenticated users are redirected to /login.

Submit button: Install Lazy Auth

On submit:
1. Save all values to auth_settings
2. Set setup_complete to true and prompt_version to 'v0.0.1'
3. Build all auth pages and components (see section 3)
4. Redirect to /admin with message: 'Lazy Auth is installed. Visit Cloud → Users → Auth → Google in Lovable to enable Google Sign-In.'

---

3. Auth pages and components

Build these pages and components:

/login
A clean, centred login page matching the site's design. Show:
- Page headline: Sign in to [brand_name]
- If google_auth_enabled: a large Sign in with Google button using the standard Google OAuth button style — white background, Google logo, dark text, rounded corners. On click trigger supabase.auth.signInWithOAuth({ provider: 'google' }).
- If email_auth_enabled: a divider line with the text 'or' between the Google button and the email form.
- If email_auth_enabled: email input and password input. A Sign in button. Below it a link: Don't have an account? Sign up.
- If magic_link_enabled: a Send magic link button below the email field. On click call supabase.auth.signInWithOtp({ email }) and show: Check your email for a login link.
- A Forgot password link that shows an email input and a Send reset link button calling supabase.auth.resetPasswordForEmail.
- Error handling: show a red inline error message if login fails. Common errors: Invalid credentials, Email not confirmed, Too many requests. Show human-readable messages not raw Supabase error codes.
- After successful login redirect to the redirect_after_login path from auth_settings.

/signup
A clean signup page. Show:
- Page headline: Create your [brand_name] account
- If google_auth_enabled: Sign up with Google button. On click trigger supabase.auth.signInWithOAuth({ provider: 'google' }). Google users skip email confirmation.
- If email_auth_enabled: full name input, email input, password input (with show/hide toggle), confirm password input, Sign up button.
- Validation: email must be valid format. Password must be at least 8 characters. Passwords must match. Show inline errors.
- On successful signup: if email confirmation is required show a message: Check your email to confirm your account. If not required redirect to redirect_after_login.
- Below the form: Already have an account? Sign in.

/account
A protected account page. Requires authentication. Redirects to /login if not signed in. Shows:
- User's avatar (Google profile photo or generated initials avatar if none), full name, and email.
- An editable full name field. Save button updates user_profiles.
- A Change password section (only shown for email/password users, not Google users): current password, new password, confirm new password. Save button calls supabase.auth.updateUser.
- A Danger zone section: Delete account button with a confirmation modal: Are you sure? This cannot be undone. On confirm call supabase.auth.admin.deleteUser and sign out.
- A Sign out button at the top right that calls supabase.auth.signOut and redirects to redirect_after_logout.

/auth/callback
A redirect handler page that Supabase and Google OAuth redirect to after authentication. Calls supabase.auth.exchangeCodeForSession, handles errors, and redirects to redirect_after_login on success or /login with an error message on failure. This page should show a loading spinner while the session is being established.

AuthGuard component
A wrapper component that protects routes. Checks if the user is authenticated using supabase.auth.getSession. If not authenticated redirect to /login with a returnTo query parameter so the user is sent back to the page they tried to visit after login. If authenticated render the children. Apply this wrapper to all routes listed in the protected_routes setting from auth_settings.

UserMenu component
A small component for the site navigation showing the current user's avatar and name when signed in, and a Sign in button when not. When signed in clicking the avatar opens a dropdown with: Account (links to /account), Sign out. Add this component to the main site navigation automatically.

useAuth hook
A React hook that exposes: user (the current Supabase user object or null), profile (the matching user_profiles row), isLoading (boolean), isAdmin (boolean — true if profile.role is admin), signOut (function). Use this hook throughout the application instead of calling Supabase auth directly.

---

4. Role-based access

If the project has an /admin route add role-based protection: only users where profile.role is 'admin' can access /admin. Any other authenticated user sees a 403 page: You do not have permission to access this page. Unauthenticated users are redirected to /login.

Add a helper function called requireRole(role) that can be used in any component to check if the current user has the required role and redirect or show an error if not.

---

5. Admin user management

Do not build a standalone dashboard. The Lazy Auth user management lives at /admin/auth as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-auth-setup.

The /admin/auth section shows:
- Total user count from user_profiles
- New users in last 7 days
- A searchable table of all user_profiles rows — columns: avatar, name, email, role, onboarded status, last seen, created date
- Click any row to open a side panel showing full profile details with an editable role selector (user / admin / moderator) and a Delete user button
- A filter row: All users, Admins, Recent (last 7 days), Never logged in
- Export CSV button that downloads all user_profiles as a CSV file

---

6. Navigation

Add Sign in and Sign up links to the main site navigation when the user is not authenticated.
Show the UserMenu component in the main site navigation when the user is authenticated.
Do not add /lazy-auth-setup to public navigation.
Add an Admin link to the main site navigation pointing to /admin — only visible when the current user is an admin.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*

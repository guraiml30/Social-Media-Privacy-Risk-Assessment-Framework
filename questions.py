"""Question bank: 20 categories x 2 questions.

Every answer option carries a risk value from 0 (safest) to 100 (most exposed).
Each question also has a `weakness` text (shown when the answer is risky) and a
`fix` text (the recommendation / checklist item).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    id: str
    category: str
    text: str
    options: tuple  # ((label, risk), ...)
    weakness: str
    fix: str


@dataclass(frozen=True)
class Category:
    id: str
    name: str
    weight: float  # importance multiplier used in the overall score
    description: str
    questions: tuple


def _cat(cid, name, weight, description, qs):
    questions = tuple(
        Question(f"{cid}_{i}", cid, text, tuple(opts), weak, fix)
        for i, (text, opts, weak, fix) in enumerate(qs, 1)
    )
    return Category(cid, name, weight, description, questions)


CATEGORIES = [
    _cat("profile_visibility", "Profile visibility", 2.0,
         "Who can see your profile and find you.", [
        ("Who can see your profile and posts by default?",
         [("Only me or close friends", 0), ("Friends / approved followers only", 20),
          ("Friends of friends", 55), ("Anyone (public)", 100)],
         "Your profile is visible to a wide audience.",
         "Set your profile to private/friends-only and check what a non-friend can see."),
        ("Can strangers find you through search engines or by your phone number/email?",
         [("No, discovery is switched off", 0), ("Limited lookup is allowed", 40),
          ("Yes, anyone can find me", 100)],
         "Strangers can discover your profile through search or contact lookup.",
         "Turn off search-engine indexing and lookup by phone/email in privacy settings."),
    ]),
    _cat("personal_info", "Personal-information exposure", 2.0,
         "Identifying details you put in your bio and posts.", [
        ("How much real personal detail is in your bio (full name, address, ID details)?",
         [("Nickname / minimal", 0), ("Some details", 45), ("Many real details", 100)],
         "Your bio contains identifying details.",
         "Trim your bio to what you would put on a public noticeboard."),
        ("Have you posted photos of tickets, boarding passes, ID cards or documents?",
         [("Never", 0), ("Once or twice, since removed", 35), ("Yes, still online", 100)],
         "Documents with barcodes or ID numbers may still be visible.",
         "Delete posts showing tickets/IDs/documents; ask the issuer to reissue if needed."),
    ]),
    _cat("contact_info", "Contact-information exposure", 2.0,
         "Email and phone visibility and reuse.", [
        ("Who can see your email address and phone number?",
         [("Nobody", 0), ("Friends only", 35), ("Anyone", 100)],
         "Your email or phone number is visible to people you may not know.",
         "Hide email and phone on your profile or set them to 'Only me'."),
        ("Do you use a separate email for social media than for banking and key accounts?",
         [("Yes, separate", 0), ("Partly", 50), ("No, same email", 100)],
         "One email links your social media to your critical accounts.",
         "Create a dedicated email for social media to limit damage from any leak."),
    ]),
    _cat("location", "Location exposure", 2.5,
         "Location tags, check-ins and routines.", [
        ("How often do your posts include your location (tags, check-ins, geotags)?",
         [("Never", 0), ("Only after I have left", 30), ("Often, in real time", 80),
          ("Almost always, including home", 100)],
         "Posts reveal where you are or live.",
         "Disable automatic location tagging; post about places only after leaving."),
        ("Do you share routine places or routes (gym, commute, fitness maps, live location)?",
         [("Never", 0), ("Sometimes", 50), ("Regularly", 100)],
         "Your routines and routes can be predicted.",
         "Hide start/end points of fitness routes; avoid live location with wide audiences."),
    ]),
    _cat("work_edu", "Workplace / education exposure", 1.5,
         "Employer, school and work-related posts.", [
        ("Who can see your employer, job title and school?",
         [("Hidden", 0), ("Friends only", 30), ("Public", 100)],
         "Employer and school details help attackers craft believable messages.",
         "Limit employer/school fields to friends or hide them."),
        ("Do you post internal work details (badges, screens, office layout, projects)?",
         [("Never", 0), ("Occasionally", 50), ("Often", 100)],
         "Work details in posts can leak confidential information.",
         "Never post badges, screens or internal documents; follow your organisation's policy."),
    ]),
    _cat("birthday", "Birthday exposure", 1.0,
         "Birth date visibility and quiz-style oversharing.", [
        ("Who can see your birth date?",
         [("Nobody", 0), ("Day/month only, friends", 30), ("Full date, friends", 60),
          ("Full date, public", 100)],
         "Your full birth date is exposed.",
         "Hide the birth year and set the date to 'Only me'."),
        ("Do you join 'fun quiz' posts (first pet, first car, school, maiden name)?",
         [("Never", 0), ("Sometimes", 60), ("Often", 100)],
         "Quiz answers are often the same as security-question answers.",
         "Skip quiz-style posts and use unrelated answers for security questions."),
    ]),
    _cat("family", "Family / relationship information", 1.5,
         "Relationship status and family details.", [
        ("Who can see your relationship status and family list?",
         [("Nobody", 0), ("Friends", 35), ("Public", 100)],
         "Family and relationship details are widely visible.",
         "Restrict relationship and family lists to 'Only me' or close friends."),
        ("Do you post names or identifiable photos of family or children publicly?",
         [("Never", 0), ("Sometimes", 50), ("Often", 100)],
         "Public family posts enable impersonation and pressure scams.",
         "Share family photos with a restricted audience; avoid full names and schools."),
    ]),
    _cat("post_visibility", "Post visibility", 2.0,
         "Default audience and posting habits.", [
        ("What is the default audience for new posts?",
         [("Only me / close friends", 0), ("Friends", 25), ("Friends of friends", 60),
          ("Public", 100)],
         "New posts default to a broad audience.",
         "Change the default post audience to Friends or narrower."),
        ("Do you review posts for sensitive details before sharing?",
         [("Always", 0), ("Sometimes", 50), ("Never", 100)],
         "Posts are shared without checking for sensitive details.",
         "Pause before posting: check backgrounds, names, locations and documents."),
    ]),
    _cat("friends_followers", "Friend / follower controls", 1.5,
         "Who can connect with you and see your connections.", [
        ("Who can send you friend or follow requests?",
         [("I approve each one manually", 0), ("Friends of friends", 40), ("Anyone", 100)],
         "Anyone can reach out and follow you.",
         "Require manual approval of followers and limit who can send requests."),
        ("Who can see your friends/followers list?",
         [("Only me", 0), ("Friends", 40), ("Public", 100)],
         "Your connections list is visible and can be used to build fake trust.",
         "Set your friends/followers list to 'Only me'."),
    ]),
    _cat("tagging", "Tagging permissions", 1.0,
         "Control over tags and mentions.", [
        ("Do you review tags before they appear on your profile?",
         [("Yes, always", 0), ("Sometimes", 50), ("No, tags appear automatically", 100)],
         "Others can attach content to your profile without approval.",
         "Turn on tag/mention review so you approve tags first."),
        ("Who can tag you in posts and photos?",
         [("Only friends I trust", 15), ("Friends of friends", 55), ("Anyone", 100)],
         "Anyone can tag you.",
         "Restrict tagging to close friends."),
    ]),
    _cat("third_party", "Third-party application access", 2.0,
         "Apps and sites connected with 'Log in with...'.", [
        ("How many apps/games/sites have access to your social account?",
         [("0-2, reviewed", 0), ("3-6", 40), ("7 or more", 80), ("I don't know", 100)],
         "Many third-party apps can access your account data.",
         "Open connected apps in settings and remove those you don't need."),
        ("How often do you review and remove unused app permissions?",
         [("Every few months", 0), ("About once a year", 40), ("Never", 100)],
         "Old app permissions remain active.",
         "Schedule a quarterly review of connected apps and permissions."),
    ]),
    _cat("authentication", "Account authentication", 3.0,
         "Password quality and device hygiene.", [
        ("How do you manage your social-media password?",
         [("Unique long passphrase in a password manager", 0),
          ("Strong, unique, memorised", 25), ("Short or simple", 80),
          ("Shared with someone", 100)],
         "Your password habits are weak.",
         "Use a password manager and a unique passphrase of 14+ characters."),
        ("Do you log in on shared/public devices or share your login?",
         [("Never", 0), ("Sometimes, and I log out", 50), ("Often stay logged in / shared", 100)],
         "Sessions may be left open on devices you don't control.",
         "Avoid shared devices; always log out and use 'log out of all sessions' if unsure."),
    ]),
    _cat("mfa", "MFA usage", 3.0,
         "Multi-factor authentication and recovery options.", [
        ("Which multi-factor authentication (MFA) do you use?",
         [("Authenticator app or security key", 0), ("SMS codes", 35),
          ("Not sure", 85), ("Not enabled", 100)],
         "MFA is missing or weak.",
         "Enable MFA with an authenticator app or a security key."),
        ("Are your recovery options (backup codes, recovery email/phone) current and secure?",
         [("Yes, backup codes stored safely", 0), ("Partly", 50), ("No / don't know", 100)],
         "Account recovery could be abused or fail.",
         "Update recovery email/phone and store backup codes in a safe place."),
    ]),
    _cat("password_reuse", "Password reuse awareness", 3.0,
         "Reuse of passwords and breach awareness.", [
        ("How often do you reuse the same password across sites?",
         [("Never", 0), ("Slight variations of one base password", 60),
          ("Same password on a few sites", 80), ("Same password on many sites", 100)],
         "Reused passwords let one breach unlock several accounts.",
         "Give every account a unique password; start with email and social accounts."),
        ("Have you checked whether your email appears in known data breaches?",
         [("Yes, and I updated passwords", 0), ("Checked long ago", 50), ("Never", 100)],
         "You may be using passwords that were already leaked.",
         "Use a reputable breach-notification service and change affected passwords."),
    ]),
    _cat("login_alerts", "Login alerts", 1.5,
         "Alerts and session monitoring.", [
        ("Are login alerts for new devices turned on?",
         [("Yes, email and app", 0), ("Only one channel", 30), ("Don't know", 80), ("No", 100)],
         "You may not notice a suspicious login.",
         "Turn on login alerts by email and in-app notification."),
        ("How often do you review active sessions and devices?",
         [("Monthly", 0), ("Occasionally", 40), ("Never", 100)],
         "Unknown devices could stay logged in.",
         "Review active sessions monthly and remove devices you don't recognise."),
    ]),
    _cat("unknown_requests", "Unknown connection requests", 2.0,
         "Handling requests from strangers.", [
        ("Do you accept friend/follow requests from people you don't know?",
         [("Never", 0), ("Only with several mutual friends", 40), ("Often", 80),
          ("Almost always", 100)],
         "Accepting strangers gives them access to your content and network.",
         "Accept only people you know; check mutual contacts for signs of fake accounts."),
        ("If someone claims a 'new account' of a friend, do you verify it?",
         [("Always, via another channel", 0), ("Sometimes", 50), ("Never", 100)],
         "Cloned-account scams can succeed against you.",
         "Confirm identity through a phone call or another channel before responding."),
    ]),
    _cat("suspicious_links", "Suspicious links / messages", 2.5,
         "Phishing and scam awareness.", [
        ("How do you handle unexpected links or attachments, even from friends?",
         [("I verify first and usually don't click", 0), ("I click if it looks familiar", 60),
          ("I usually click", 100)],
         "Unverified links are a common route to account takeover.",
         "Don't click unexpected links; open the official app/site yourself instead."),
        ("Do you know how to report scam/phishing messages on your platform?",
         [("Yes, and I use it", 0), ("Aware but haven't used it", 40), ("No", 100)],
         "You may not report scams, leaving others exposed.",
         "Learn the report/block flow and use it for every suspicious message."),
    ]),
    _cat("photo_metadata", "Photo metadata awareness", 1.0,
         "Hidden data (EXIF) inside photos.", [
        ("Do you know photos can contain hidden metadata (GPS, device, time)?",
         [("Yes, and I disable camera geotagging", 0), ("Yes, but I do nothing", 50), ("No", 100)],
         "Photos may carry hidden location data.",
         "Turn off geotagging in your camera app and strip metadata before sharing files."),
        ("Do you share original photo files directly (not compressed uploads) publicly?",
         [("Never", 0), ("Sometimes", 60), ("Often", 100)],
         "Original files can include GPS and device details.",
         "Share compressed or metadata-stripped copies; use platform uploads."),
    ]),
    _cat("historical_posts", "Historical posts", 1.5,
         "Old content that may still be visible.", [
        ("When did you last audit your old posts?",
         [("Within the last year", 0), ("More than a year ago", 50), ("Never", 100)],
         "Old posts may contain outdated or sensitive information.",
         "Audit old posts yearly and delete anything sensitive or embarrassing."),
        ("Are your old posts limited to a restricted audience?",
         [("Yes", 0), ("Some of them", 50), ("No, all still visible", 100)],
         "Years of old content remain visible.",
         "Use the 'limit past posts' setting and bulk-archive older content."),
    ]),
    _cat("social_engineering", "Social-engineering exposure", 2.5,
         "How much an attacker could learn and exploit.", [
        ("How much about your routine, travel plans and relationships is posted?",
         [("Very little", 0), ("Some", 50), ("A lot", 100)],
         "Enough detail is public to make a convincing impersonation or scam.",
         "Avoid posting travel plans in advance; post trips after returning."),
        ("If a message creates urgency (locked account, prize, family emergency), what do you do?",
         [("Pause and verify via official channels", 0), ("Sometimes act quickly", 60),
          ("Act immediately", 100)],
         "Urgency is the main tool in scams and you may act on it.",
         "Adopt a pause-and-verify rule: no money, codes or logins under pressure."),
    ]),
]

QUESTIONS = {q.id: q for c in CATEGORIES for q in c.questions}
CATEGORY_BY_ID = {c.id: c for c in CATEGORIES}

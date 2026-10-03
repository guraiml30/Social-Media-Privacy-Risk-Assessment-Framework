"""Streamlit UI: python -m streamlit run app.py"""
import pandas as pd
import streamlit as st

from privacy_framework import DISCLAIMER, LEVELS
from privacy_framework.awareness import LEVEL_GUIDANCE, TIPS, RED_FLAGS
from privacy_framework.questions import CATEGORIES, QUESTIONS
from privacy_framework.recommendations import build_recommendations, build_checklist
from privacy_framework.report import build_markdown, build_html
from privacy_framework.scoring import score_assessment
from privacy_framework.synthetic import ARCHETYPES, demo_answers, generate_profiles

ICON = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}

st.set_page_config(page_title="Social Media Privacy Risk Framework", page_icon="🛡️", layout="wide")
page = st.sidebar.radio("Menu", ["Assessment", "Dashboard (synthetic)", "Awareness", "About"])
st.sidebar.info("Educational tool. Use demo answers only - nothing is stored.")


def load_persona(archetype):
    answers = demo_answers(archetype)
    for qid, q in QUESTIONS.items():
        st.session_state[qid] = q.options[answers[qid]][0]
    st.session_state.pop("result", None)


def clear_answers():
    for qid in QUESTIONS:
        st.session_state[qid] = None
    st.session_state.pop("result", None)


def show_result(res):
    st.header(f"{ICON[res.level]} Privacy Risk Score: {res.overall}/100 - {res.level}")
    st.caption("Higher score = higher exposure. " + LEVEL_GUIDANCE[res.level])
    st.progress(res.overall / 100)
    if res.compound:
        for c in res.compound:
            st.warning(c["message"])

    names = {c.id: c.name for c in CATEGORIES}
    df = pd.DataFrame({"Category": [names[k] for k in res.category_scores],
                       "Score": list(res.category_scores.values())}).set_index("Category")
    st.subheader("Category scores")
    st.bar_chart(df)

    st.subheader("Detected weaknesses")
    if res.weaknesses:
        st.dataframe(pd.DataFrame(res.weaknesses)[
            ["severity", "category_name", "weakness", "answer"]], use_container_width=True)
    else:
        st.success("No weaknesses detected.")

    st.subheader("Personalised recommendations")
    for r in build_recommendations(res):
        st.markdown(f"**{r['priority']}** - *{r['category']}*: {r['action']}")

    with st.expander("Privacy checklist"):
        for i in build_checklist(res):
            st.markdown(f"{'✅' if i['done'] else '⬜'} {i['item']}")

    st.subheader("Download report")
    c1, c2 = st.columns(2)
    c1.download_button("Markdown", build_markdown(res), "privacy_report.md")
    c2.download_button("HTML", build_html(res), "privacy_report.html", mime="text/html")


if page == "Assessment":
    st.title("🛡️ Social Media Privacy Risk Assessment")
    st.warning(DISCLAIMER)
    b1, b2, b3 = st.columns(3)
    b1.button("Load random fictional persona", on_click=load_persona, args=(None,))
    b2.button("Load 'oversharer' persona", on_click=load_persona, args=("oversharer",))
    b3.button("Clear answers", on_click=clear_answers)

    with st.form("assessment"):
        for c in CATEGORIES:
            with st.expander(f"{c.name} - {c.description}"):
                for q in c.questions:
                    st.radio(q.text, [o[0] for o in q.options], index=None, key=q.id)
        submitted = st.form_submit_button("Calculate my privacy risk")

    if submitted:
        answers, missing = {}, 0
        for qid, q in QUESTIONS.items():
            choice = st.session_state.get(qid)
            if choice is None:
                missing += 1
            else:
                answers[qid] = [o[0] for o in q.options].index(choice)
        if missing:
            st.error(f"Please answer all questions ({missing} left) or load a demo persona.")
        else:
            st.session_state["result"] = score_assessment(answers)
    if "result" in st.session_state:
        show_result(st.session_state["result"])

elif page == "Dashboard (synthetic)":
    st.title("📊 Aggregate dashboard")
    st.info("All data here is synthetic: randomly generated fictional profiles.")

    @st.cache_data
    def load():
        return pd.DataFrame(generate_profiles(300, seed=42))

    df = load()
    m1, m2, m3 = st.columns(3)
    m1.metric("Profiles", len(df))
    m2.metric("Average score", round(df["overall"].mean(), 1))
    m3.metric("HIGH or CRITICAL", f"{(df['level'].isin(['HIGH', 'CRITICAL'])).mean():.0%}")

    st.subheader("Risk level distribution")
    st.bar_chart(df["level"].value_counts().reindex(LEVELS, fill_value=0))

    st.subheader("Average score by category")
    names = {c.id: c.name for c in CATEGORIES}
    cat = df[[f"cat_{c.id}" for c in CATEGORIES]].mean()
    cat.index = [names[i.replace("cat_", "")] for i in cat.index]
    st.bar_chart(cat)

    st.subheader("Average score by archetype")
    st.bar_chart(df.groupby("archetype")["overall"].mean())

    st.subheader("Most common weaknesses")
    ids = df["weaknesses"].fillna("").str.split("|").explode()
    top = ids[ids != ""].value_counts().head(10)
    top.index = [QUESTIONS[i].weakness for i in top.index]
    st.bar_chart(top)

elif page == "Awareness":
    st.title("📚 Security awareness")
    for title, body in TIPS:
        st.markdown(f"**{title}** - {body}")
    st.subheader("Scam red flags")
    for r in RED_FLAGS:
        st.markdown(f"- {r}")

else:
    st.title("About")
    st.markdown(
        "**Method:** 20 categories x 2 questions. Each answer has a risk value 0-100. "
        "Category score = average; overall = weighted average of categories + a small bonus "
        "(max 15) when risky habits combine.\n\n"
        "**Levels:** 0-20 LOW, 21-40 MODERATE, 41-70 HIGH, 71-100 CRITICAL.\n\n"
        "**Ethics:** no scraping, no real profiles, no tracking of individuals.")
    st.warning(DISCLAIMER)

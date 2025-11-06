import streamlit as st
import time
import json
from datetime import datetime, timedelta
from agents.planner import PlannerAgent
from agents.quiz import QuizAgent
from agents.advice import AdviceAgent

# Initialize agents
planner_agent = PlannerAgent()
quiz_agent = QuizAgent()
advice_agent = AdviceAgent()

# Page configuration
st.set_page_config(
    page_title="🎓 AI Study Coach Dashboard",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
defaults = {
    "plan": None,
    "topic": "",
    "days": 1,
    "hours": 1,
    "quiz_data": None,
    "quiz_running": False,
    "current_q": 0,
    "user_answers": {},
    "q_start_time": None,
    "quiz_completed": False,
    "quiz_history": [],  # Store quiz results
    "total_quizzes": 0,
    "total_score": 0,
    "study_streak": 0,
    "last_study_date": None
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/book.png", width=80)
    st.title("📚 Navigation")
    
    page = st.radio(
        "Go to:",
        ["🏠 Dashboard", "📖 Study Planner", "🧩 Take Quiz", "📊 Progress Analytics", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Quick Stats in Sidebar
    st.subheader("Quick Stats")
    st.metric("Total Quizzes", st.session_state.total_quizzes)
    avg_score = (st.session_state.total_score / st.session_state.total_quizzes * 100) if st.session_state.total_quizzes > 0 else 0
    st.metric("Average Score", f"{avg_score:.1f}%")
    st.metric("Study Streak", f"{st.session_state.study_streak} days")

# ================== DASHBOARD PAGE ==================
if page == "🏠 Dashboard":
    st.markdown('<p class="main-header">🎓 AI Study Coach</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your personalized learning companion</p>', unsafe_allow_html=True)
    
    # Welcome message
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Today's Goal")
        if st.session_state.plan:
            st.success(f"Study: {st.session_state.topic}")
            st.info(f"📅 {st.session_state.days} days | ⏰ {st.session_state.hours}h/day")
        else:
            st.warning("No active study plan")
            if st.button("Create Plan Now"):
                page = "📖 Study Planner"
                st.rerun()
    
    with col2:
        st.markdown("### 📈 Recent Performance")
        if st.session_state.quiz_history:
            last_quiz = st.session_state.quiz_history[-1]
            score_pct = (last_quiz['score'] / last_quiz['total']) * 100
            st.metric("Last Quiz Score", f"{last_quiz['score']}/{last_quiz['total']}", f"{score_pct:.0f}%")
        else:
            st.info("No quizzes taken yet")
    
    with col3:
        st.markdown("### 🔥 Motivation")
        motivational_quotes = [
            "Keep learning, keep growing! 🌱",
            "Small steps lead to big results! 🚀",
            "You're doing great! Keep it up! ⭐",
            "Knowledge is power! 💪",
            "Stay focused, stay strong! 🎯"
        ]
        import random
        st.success(random.choice(motivational_quotes))
    
    st.divider()
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📖 Create Study Plan", use_container_width=True):
            st.session_state.page = "📖 Study Planner"
            st.rerun()
    
    with col2:
        if st.button("🧩 Take Quiz", use_container_width=True):
            st.session_state.page = "🧩 Take Quiz"
            st.rerun()
    
    with col3:
        if st.button("📊 View Progress", use_container_width=True):
            st.session_state.page = "📊 Progress Analytics"
            st.rerun()
    
    with col4:
        if st.button("💡 Get Advice", use_container_width=True):
            if st.session_state.quiz_history:
                with st.spinner("Getting advice..."):
                    last_quiz = st.session_state.quiz_history[-1]
                    advice = advice_agent.give_advice(
                        topic=last_quiz['topic'],
                        score=last_quiz['score'],
                        total=last_quiz['total'],
                        plan_summary=st.session_state.plan[:400] if st.session_state.plan else None
                    )
                    st.info(advice)
            else:
                st.warning("Take a quiz first to get personalized advice!")
    
    # Recent Activity
    st.divider()
    st.markdown("### 📋 Recent Activity")
    
    if st.session_state.quiz_history:
        for quiz in reversed(st.session_state.quiz_history[-5:]):
            with st.expander(f"📝 {quiz['topic']} - {quiz['date']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Score:** {quiz['score']}/{quiz['total']}")
                    st.write(f"**Accuracy:** {(quiz['score']/quiz['total']*100):.1f}%")
                with col2:
                    st.write(f"**Time:** {quiz.get('duration', 'N/A')}")
                    level = "🟢 Advanced" if quiz['score']/quiz['total'] >= 0.8 else "🟡 Intermediate" if quiz['score']/quiz['total'] >= 0.5 else "🔴 Beginner"
                    st.write(f"**Level:** {level}")
    else:
        st.info("No activity yet. Start by creating a study plan!")

# ================== STUDY PLANNER PAGE ==================
elif page == "📖 Study Planner":
    st.title("📖 Study Plan Generator")
    st.write("Create a personalized study plan tailored to your goals")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("📚 What do you want to study?", st.session_state.topic, 
                             placeholder="e.g., Python Programming, World History, Calculus")
    
    with col2:
        difficulty = st.selectbox("🎯 Difficulty Level", 
                                 ["Beginner", "Intermediate", "Advanced"])
    
    col1, col2 = st.columns(2)
    with col1:
        days = st.number_input("🗓️ Number of days:", 1, 60, st.session_state.days)
    with col2:
        hours = st.number_input("⏰ Hours per day:", 1, 12, st.session_state.hours)
    
    if st.button("🚀 Generate Study Plan", use_container_width=True, type="primary"):
        if topic:
            with st.spinner("🧠 Creating your personalized study plan..."):
                enhanced_prompt = f"{topic} (Difficulty: {difficulty})"
                st.session_state.plan = planner_agent.create_plan(enhanced_prompt, days, hours)
                st.session_state.topic = topic
                st.session_state.days = days
                st.session_state.hours = hours
                st.session_state.quiz_data = None
                st.session_state.quiz_running = False
                st.session_state.quiz_completed = False
                st.balloons()
                st.success("✅ Study Plan Created Successfully!")
                st.markdown("---")
                st.markdown(st.session_state.plan)
        else:
            st.warning("⚠️ Please enter a topic first!")
    
    # Display existing plan
    if st.session_state.plan and st.session_state.topic:
        st.divider()
        st.markdown("### 📋 Current Study Plan")
        st.info(f"**Topic:** {st.session_state.topic} | **Duration:** {st.session_state.days} days | **Daily Hours:** {st.session_state.hours}")
        with st.expander("📖 View Full Plan", expanded=False):
            st.markdown(st.session_state.plan)

# ================== QUIZ PAGE ==================
elif page == "🧩 Take Quiz":
    st.title("🧩 Interactive Quiz")
    
    if not st.session_state.plan:
        st.warning("⚠️ Please create a study plan first!")
        if st.button("Go to Study Planner"):
            st.session_state.page = "📖 Study Planner"
            st.rerun()
    else:
        if not st.session_state.quiz_running and not st.session_state.quiz_completed:
            st.info(f"📚 Ready to test your knowledge on **{st.session_state.topic}**?")
            
            col1, col2 = st.columns(2)
            with col1:
                num_questions = st.slider("Number of Questions", 3, 10, 5)
            with col2:
                time_per_q = st.slider("Time per Question (seconds)", 10, 30, 15)
            
            if st.button("🎯 Start Quiz", use_container_width=True, type="primary"):
                with st.spinner("Generating quiz..."):
                    quiz_data = quiz_agent.generate_quiz(st.session_state.topic, num_questions)
                if quiz_data:
                    st.session_state.quiz_data = quiz_data
                    st.session_state.quiz_running = True
                    st.session_state.current_q = 0
                    st.session_state.user_answers = {}
                    st.session_state.q_start_time = None
                    st.session_state.quiz_completed = False
                    st.session_state.quiz_start_time = time.time()
                    st.session_state.time_per_q = time_per_q
                    st.rerun()
                else:
                    st.error("⚠️ Couldn't generate quiz. Please try again.")
        
        # Quiz Execution
        if st.session_state.quiz_running and st.session_state.quiz_data and not st.session_state.quiz_completed:
            quiz = st.session_state.quiz_data
            total_q = len(quiz)
            qidx = st.session_state.current_q
            
            if qidx < total_q:
                q = quiz[qidx]
                
                if st.session_state.q_start_time is None:
                    st.session_state.q_start_time = time.time()
                
                elapsed = time.time() - st.session_state.q_start_time
                duration = st.session_state.get('time_per_q', 15.0)
                remaining = max(0, duration - elapsed)
                
                # Progress
                st.progress((qidx) / total_q, text=f"Question {qidx + 1} of {total_q}")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### Q{qidx + 1}. {q['question']}")
                with col2:
                    st.metric("⏱️ Time Left", f"{int(remaining)}s")
                
                choice_key = f"timed_q_{qidx}"
                selected = st.radio(
                    "Select your answer:",
                    q["options"],
                    key=choice_key,
                    index=None
                )
                if selected:
                    st.session_state.user_answers[qidx] = selected
                
                if elapsed >= duration:
                    if qidx not in st.session_state.user_answers:
                        st.session_state.user_answers[qidx] = ""
                    st.session_state.current_q += 1
                    st.session_state.q_start_time = None
                    st.rerun()
                else:
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.session_state.quiz_running = False
                st.session_state.quiz_completed = True
                st.session_state.q_start_time = None
                st.rerun()
        
        # Quiz Results
        if st.session_state.quiz_completed and st.session_state.quiz_data:
            st.success("✅ Quiz Completed!")
            
            quiz = st.session_state.quiz_data
            score = 0
            
            st.markdown("### 📊 Your Results")
            
            for i, q in enumerate(quiz):
                user_ans = st.session_state.user_answers.get(i, "")
                correct = q["answer"]
                if user_ans == correct:
                    score += 1
                    st.success(f"✅ **Q{i + 1}:** {q['question']}")
                    st.write(f"Your answer: **{correct}**")
                else:
                    st.error(f"❌ **Q{i + 1}:** {q['question']}")
                    st.write(f"Your answer: **{user_ans or 'No answer'}** | Correct: **{correct}**")
            
            # Save to history
            quiz_duration = time.time() - st.session_state.get('quiz_start_time', time.time())
            quiz_record = {
                'topic': st.session_state.topic,
                'score': score,
                'total': len(quiz),
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'duration': f"{int(quiz_duration)}s"
            }
            
            if quiz_record not in st.session_state.quiz_history:
                st.session_state.quiz_history.append(quiz_record)
                st.session_state.total_quizzes += 1
                st.session_state.total_score += score
            
            # Display score
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score}/{len(quiz)}")
            with col2:
                accuracy = (score / len(quiz)) * 100
                st.metric("Accuracy", f"{accuracy:.1f}%")
            with col3:
                st.metric("Time Taken", f"{int(quiz_duration)}s")
            
            # Personalized Advice
            with st.spinner("🧭 Generating personalized advice..."):
                advice = advice_agent.give_advice(
                    topic=st.session_state.topic,
                    score=score,
                    total=len(quiz),
                    plan_summary=st.session_state.plan[:400] if st.session_state.plan else None
                )
            
            st.markdown("### 💬 Study Coach Advice")
            st.info(advice)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Take Another Quiz", use_container_width=True):
                    st.session_state.quiz_data = None
                    st.session_state.quiz_running = False
                    st.session_state.quiz_completed = False
                    st.session_state.current_q = 0
                    st.session_state.user_answers = {}
                    st.rerun()
            with col2:
                if st.button("📊 View Analytics", use_container_width=True):
                    st.session_state.page = "📊 Progress Analytics"
                    st.rerun()

# ================== ANALYTICS PAGE ==================
elif page == "📊 Progress Analytics":
    st.title("📊 Progress Analytics")
    
    if not st.session_state.quiz_history:
        st.info("No quiz data yet. Take some quizzes to see your progress!")
    else:
        # Overall Stats
        col1, col2, col3, col4 = st.columns(4)
        
        total_quizzes = len(st.session_state.quiz_history)
        total_questions = sum(q['total'] for q in st.session_state.quiz_history)
        total_correct = sum(q['score'] for q in st.session_state.quiz_history)
        avg_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        with col1:
            st.metric("Total Quizzes", total_quizzes)
        with col2:
            st.metric("Questions Answered", total_questions)
        with col3:
            st.metric("Correct Answers", total_correct)
        with col4:
            st.metric("Avg. Accuracy", f"{avg_accuracy:.1f}%")
        
        st.divider()
        
        # Performance Chart
        st.markdown("### 📈 Performance Over Time")
        
        chart_data = []
        for i, quiz in enumerate(st.session_state.quiz_history):
            accuracy = (quiz['score'] / quiz['total']) * 100
            chart_data.append({
                'Quiz': i + 1,
                'Accuracy': accuracy,
                'Topic': quiz['topic']
            })
        
        import pandas as pd
        df = pd.DataFrame(chart_data)
        st.line_chart(df.set_index('Quiz')['Accuracy'])
        
        # Detailed History
        st.markdown("### 📋 Quiz History")
        for i, quiz in enumerate(reversed(st.session_state.quiz_history)):
            accuracy = (quiz['score'] / quiz['total']) * 100
            
            with st.expander(f"Quiz #{total_quizzes - i}: {quiz['topic']} - {quiz['date']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Score", f"{quiz['score']}/{quiz['total']}")
                with col2:
                    st.metric("Accuracy", f"{accuracy:.1f}%")
                with col3:
                    st.metric("Duration", quiz.get('duration', 'N/A'))

# ================== SETTINGS PAGE ==================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.markdown("### 🎨 Preferences")
    
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
    
    st.markdown("### 📊 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Progress", use_container_width=True):
            data = json.dumps(st.session_state.quiz_history, indent=2)
            st.download_button(
                label="Download JSON",
                data=data,
                file_name="study_progress.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            if st.checkbox("I confirm I want to delete all data"):
                st.session_state.quiz_history = []
                st.session_state.total_quizzes = 0
                st.session_state.total_score = 0
                st.success("All data cleared!")
                st.rerun()
    
    st.markdown("### ℹ️ About")
    st.info("""
    **AI Study Coach Dashboard v1.0**
    
    Created with Streamlit and Groq AI
    
    Features:
    - Personalized study plans
    - Timed interactive quizzes
    - Progress tracking & analytics
    - AI-powered advice
    """)
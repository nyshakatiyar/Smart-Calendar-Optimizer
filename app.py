import streamlit as st
import numpy as np
from calendar_core import SmartScheduler
from google_integration import GoogleCalendarManager

# ===== WIDE LAYOUT CONFIG =====
st.set_page_config(
    page_title="Smart Calendar Optimizer",
    layout="wide",  # <-- THIS MAKES IT WIDE
    initial_sidebar_state="expanded"
)

# Custom CSS for better spacing
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stSlider {
        padding: 0 1rem;
    }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    .event-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
    }
    .event-name {
        font-weight: 600;
        font-size: 1.1rem;
        color: #2c3e50;
    }
    .event-time {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize services
    scheduler = SmartScheduler()
    calendar_manager = GoogleCalendarManager()

    # ===== MAIN COLUMNS =====
    col1, col2 = st.columns([1, 2])  # Wider right column

    with col1:
        st.title("📅 Smart Calendar Pro")
        st.write("AI-powered scheduling optimized for your preferences")

        # ===== SETTINGS =====
        with st.expander("⚙️ Settings", expanded=True):
            num_events = st.number_input("Number of Events", 1, 20, 2)
            num_slots = st.number_input("Number of Time Slots", 1, 20, 3)

        # ===== EVENT DETAILS =====
        st.subheader("📝 Event Details")
        events = [st.text_input(f"Event {i+1} Name", f"Event {i+1}", key=f"event_{i}") 
                 for i in range(num_events)]

    with col2:
        # ===== TIME SLOTS =====
        st.subheader("⏰ Time Slots")
        time_cols = st.columns(num_slots)
        default_times = ["9:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"]
        time_slots = []
        
        for i in range(num_slots):
            with time_cols[i]:
                time_slots.append(st.text_input(
                    f"Slot {i+1}",
                    default_times[i] if i < len(default_times) else "",
                    key=f"time_{i}"
                ))

        # ===== PREFERENCES GRID =====
        st.subheader("📊 Preference Matrix")
        st.info("Rate each time slot (1 = Best, 10 = Worst)")
        
        preferences = np.zeros((num_events, num_slots))
        grid = st.columns(num_slots + 1)
        
        # Header row
        with grid[0]:
            st.markdown("**Event**")
        for j in range(num_slots):
            with grid[j+1]:
                st.markdown(f"**{time_slots[j]}**")
        
        # Preference sliders
        for i in range(num_events):
            grid = st.columns(num_slots + 1)
            with grid[0]:
                st.markdown(f"{events[i]}")
            for j in range(num_slots):
                with grid[j+1]:
                    preferences[i,j] = st.slider(
                        f"{events[i]} @ {time_slots[j]}",
                        1, 10, 5,
                        key=f"pref_{i}_{j}",
                        label_visibility="collapsed"
                    )

    # ===== SCHEDULE GENERATION =====
    if st.button("✨ Generate Optimal Schedule", type="primary"):
        with st.spinner("Optimizing your schedule..."):
            try:
                schedule, score = scheduler.optimize(events, time_slots, preferences)
                
                st.success("✅ Schedule optimized successfully!")
                
                # Display schedule in a nice card layout
                cols = st.columns(len(schedule))
                for idx, (event, slot) in enumerate(zip(events, schedule)):
                    with cols[idx]:
                        st.markdown(f"""
                        <div style='
                            padding: 1rem;
                            border-radius: 0.5rem;
                            background: #f0f2f6;
                            margin-bottom: 1rem;
                        '>
                            <h4>{event}</h4>
                            <p>⏰ {slot}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.metric("Optimization Score", score)
                
                # Store results
                st.session_state.events = events
                st.session_state.schedule = schedule
                
            except Exception as e:
                st.error(f"❌ Error generating schedule: {str(e)}")

    # ===== GOOGLE CALENDAR INTEGRATION =====
    if 'schedule' in st.session_state:
        st.divider()
        st.subheader("📤 Calendar Integration")
        
        days_ahead = st.number_input("Schedule for days from today", 0, 30, 0)
        
        if st.button("🗓️ Add to Google Calendar", use_container_width=True):
            with st.spinner("Adding to Google Calendar..."):
                results = calendar_manager.add_events(
                    st.session_state.events,
                    st.session_state.schedule,
                    days_ahead
                )
                
                for result in results:
                    if result['status'] == 'success':
                        st.success(f"✅ Added {result['event']} at {result['time']} [View Event]({result['link']})")
                    else:
                        st.error(f"❌ Failed to add {result['event']}: {result['error']}")

if __name__ == "__main__":
    main()
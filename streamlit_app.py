import streamlit as st
import warnings
import json
from datetime import datetime
import uuid
from services.analysis_service import analysis_service
from database.manager import db_manager

warnings.filterwarnings("ignore", category=Warning)

def init_session_state():
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 1
    if 'case_text' not in st.session_state:
        st.session_state.case_text = ""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

async def analyze_stage(text, stage):
    try:
        result = await analysis_service.analyze_single_stage(text, stage)
        return result
    except Exception as e:
        st.error(f"حدث خطأ في تحليل المرحلة {stage}: {str(e)}")
        return None

def save_case_results(text, stages):
    try:
        case_id = str(uuid.uuid4())
        formatted_stages = {}
        
        for stage_num, stage_data in stages.items():
            formatted_stages[stage_num] = {
                'content': stage_data,
                'status': 'completed',
                'model': 'groq' if int(stage_num) in [1, 3, 5, 7] else 'gemini',
                'timestamp': datetime.now().isoformat()
            }

        case_data = {
            'id': case_id,
            'title': text[:100] + '...' if len(text) > 100 else text,
            'original_text': text,
            'stages': json.dumps(formatted_stages),
            'status': 'completed',
            'date': datetime.now().isoformat()
        }

        db_manager.save_case(case_data)
        return case_id
    except Exception as e:
        st.error(f"حدث خطأ في حفظ القضية: {str(e)}")
        return None

def main():
    st.title("نظام تحليل القضايا الجنائية")
    init_session_state()

    # القائمة الجانبية
    with st.sidebar:
        st.header("القضايا المكتملة")
        cases = db_manager.get_all_cases()
        for case in cases:
            if st.button(f"قضية: {case['title'][:50]}...", key=case['id']):
                st.session_state.selected_case = case

    # نموذج إدخال النص
    case_text = st.text_area(
        "أدخل نص القضية هنا",
        value=st.session_state.case_text,
        height=200
    )

    if st.button("بدء التحليل"):
        if not case_text:
            st.warning("الرجاء إدخال نص القضية أولاً")
            return

        st.session_state.case_text = case_text
        st.session_state.current_stage = 1
        st.session_state.analysis_results = {}

    # عرض مراحل التحليل
    if st.session_state.case_text:
        stages_description = {
            1: "تحليل الوقائع والأحداث",
            2: "تحديد الأطراف المعنية",
            3: "تحليل الأدلة والقرائن",
            4: "تحديد الظروف المحيطة",
            5: "تحليل الدوافع والأسباب",
            6: "تقييم المسؤولية القانونية",
            7: "تحليل الآثار والنتائج",
            8: "التوصيات والإجراءات المقترحة"
        }

        current_stage = st.session_state.current_stage
        
        if current_stage <= 8:
            with st.spinner(f"جاري تحليل المرحلة {current_stage}: {stages_description[current_stage]}"):
                result = analyze_stage(st.session_state.case_text, current_stage)
                if result:
                    st.session_state.analysis_results[current_stage] = result
                    st.success(f"اكتملت المرحلة {current_stage}")
                    st.write(result)
                    
                    if current_stage < 8:
                        st.session_state.current_stage += 1
                    else:
                        case_id = save_case_results(
                            st.session_state.case_text,
                            st.session_state.analysis_results
                        )
                        if case_id:
                            st.success("تم حفظ القضية بنجاح!")
                            st.balloons()

        # عرض نتائج التحليل السابقة
        for stage_num in range(1, current_stage):
            if stage_num in st.session_state.analysis_results:
                with st.expander(f"نتائج المرحلة {stage_num}: {stages_description[stage_num]}"):
                    st.write(st.session_state.analysis_results[stage_num])

if __name__ == "__main__":
    main() 
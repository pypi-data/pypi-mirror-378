from datetime import datetime

from tau_trait.types import Task, Action
from tau_trait.envs.telehealth.data import load_data

def _format_currency(value: float) -> str:
    """Return a 2-decimal string for currency comparisons."""
    return f"{value:.2f}"


def _next_appointment_id(appointments: dict[str, dict]) -> str:
    """Replicate the ID generation used by schedule_appointment."""
    existing_ids = [
        int(appt_id.replace("APPT", ""))
        for appt_id in appointments
        if appt_id.startswith("APPT") and appt_id[4:].isdigit()
    ]
    new_id_num = max(existing_ids) + 1 if existing_ids else 1
    return f"APPT{new_id_num:03d}"


def _task_three_outputs() -> list[str]:
    data = load_data()
    patient = data["patients"]["maria_rodriguez_4567"]
    appointments = data["appointments"]
    existing_link = appointments["APPT007"]["meeting_link"]
    new_appointment_id = _next_appointment_id(appointments)
    insurance = patient["insurance"]["primary"]
    primary_copay = insurance["copay_primary"]
    specialist_copay = insurance["copay_specialist"]
    return [
        _format_currency(primary_copay),
        _format_currency(specialist_copay),
        existing_link,
        f"https://telehealth.healthcenter.com/room/{new_appointment_id}",
    ]


def _task_nine_outputs() -> list[str]:
    data = load_data()
    appointments = data["appointments"]
    patient = data["patients"]["maria_rodriguez_4567"]
    specialist_copay = patient["insurance"]["primary"]["copay_specialist"]
    new_appointment_id = _next_appointment_id(appointments)
    return [
        _format_currency(specialist_copay),
        f"https://telehealth.healthcenter.com/room/{new_appointment_id}",
    ]


def _task_eleven_outputs() -> list[str]:
    return [
        "Triveni Pharma (India)",
        "Setrina",
        "$4.55",
        "Delhi ZenLabs (India)",
        "Zenpira",
        "$3.05",
        "Lotus Breath (India)",
        "BreathFree",
        "Lotus Respiratory (India)",
        "Flohale",
        "$7.10",
        "Aurora Heart Labs (India)",
        "BetaShield",
        "$3.80",
        "Mumbai Care Labs (India)",
        "CardiShield 81",
        "$1.85",
        "VedaRx Labs (India)",
        "Atorveeda",
        "$4.05",
    ]


def _task_twelve_outputs() -> list[str]:
    data = load_data()
    interactions = data["drug_interactions"]

    primary = "Sertraline"
    baseline_meds = ["Warfarin", "Metoprolol", "Simvastatin", "Aspirin"]

    severity_rank = {"low": 1, "moderate": 2, "high": 3}
    emergency = False
    skip_set: set[str] = set()
    max_overlap = 0
    summaries: list[str] = []
    highest_pair = None
    highest_severity = "none"

    def lookup(med_a: str, med_b: str):
        med_a_data = interactions.get(med_a, {})
        if med_b in med_a_data:
            return med_a_data[med_b]
        med_b_data = interactions.get(med_b, {})
        return med_b_data.get(med_a)

    def register_pair(med_a: str, med_b: str):
        nonlocal emergency, max_overlap, highest_pair, highest_severity
        details = lookup(med_a, med_b)
        if not details:
            return
        severity = details.get("severity", "unknown")
        risk = details.get("risk_score")
        overlap = details.get("time_overlap_hours", 0)
        action = details.get("action", "Monitor.")
        skip_set.update(details.get("skip", []))
        emergency = emergency or details.get("emergency", False)
        max_overlap = max(max_overlap, overlap)
        summaries.append(
            f"{med_a} + {med_b}: severity={severity}, risk_score={risk}, overlap_hours={overlap}. {action}"
        )
        if severity_rank.get(severity, 0) > severity_rank.get(highest_severity, 0):
            highest_severity = severity
            highest_pair = f"{med_a} + {med_b}"

    for med in baseline_meds:
        register_pair(primary, med)

    for idx, med_a in enumerate(baseline_meds):
        for med_b in baseline_meds[idx + 1 :]:
            register_pair(med_a, med_b)

    skip_list = sorted(skip_set)
    emergency_text = "Yes" if emergency else "No"
    outputs = [
        f"Emergency escalation required: {emergency_text}",
        f"Medications to hold today: {', '.join(skip_list) if skip_list else 'None'}",
        f"Peak overlap risk window (hours): {max_overlap}",
        "Hold the next warfarin dose, monitor INR, and seek urgent clinical guidance.",
        "Hold aspirin for 24 hours and observe for bleeding.",
        "Monitor for bradycardia; no dose adjustment typically needed.",
        "Advise hydration and routine symptom watch.",
        "If combined with serotonergic agents, hold aspirin for one cycle and contact cardiology.",
    ]
    return outputs


TASKS_TEST = [
    Task(
        annotator="0",
        user_id="sarah_johnson_1234",
        instruction="""
        You are Sarah Johnson, born March 15, 1985. 
        You want to schedule a follow-up appointment on Tuesday, September 23, 2025 at 10:00 AM 
        with your primary care doctor Dr. Garcia to discuss your blood pressure medication.
        """,
        actions=[
            Action(name="schedule_appointment", kwargs={"patient_id": "sarah_johnson_1234", "provider_id": "dr_garcia_primary", "date": "2025-09-23", "time": "10:00", "appointment_type": "follow_up"}),
        ],
        outputs= [],
    ),
    Task(
        annotator="1",
        user_id="david_martinez_5678",
        instruction="""
        You are David Martinez, email david.martinez@email.com. 
        You want to schedule a consultation appointment on Monday, September 22, 2025 at 2:00 PM (14:00) 
        with Dr. Smith (the cardiologist) to discuss your heart palpitations. However, if Dr. Smith is not 
        available at that exact time, you are willing to schedule with Dr. Garcia (your primary care doctor) 
        at the same time instead. You need to check both doctors' availability and schedules first.
        """,
        actions=[
            Action(name="find_patient_by_email", kwargs={"email": "david.martinez@email.com"}),
            Action(name="get_provider_details", kwargs={"provider_id": "dr_smith_cardiology"}),
            Action(name="get_provider_details", kwargs={"provider_id": "dr_garcia_primary"}),
            Action(name="schedule_appointment", kwargs={"patient_id": "david_martinez_5678", "provider_id": "dr_garcia_primary", "date": "2025-09-22", "time": "14:00", "appointment_type": "consultation"}),
        ],
        outputs=[],
    ),
    Task(
        annotator="2",
        user_id="maria_rodriguez_4567",
        instruction="""
        You are Maria Rodriguez, born December 3, 1990. You have a complex scheduling situation:
        
        1. You currently have appointment APPT007 with Dr. Garcia on Monday, January 22nd 2025 at 9:00 AM
        2. You need to reschedule it because you have a work conflict, but you can only meet on the same day (Monday) at 3:00 PM or later.
        3. You also need to schedule a separate specialist cardiology consultation for your new heart palpitations, preferably with the most experienced cardiologist available
        4. The cardiology appointment must be on Tuesday, January 23rd 2025 at exactly 09:00 (9:00 AM) so it is finished before work
        5. You want to verify your insurance copays for both appointments before confirming
        7. You need to get the meeting links for both final appointments
        
        Complete ALL requirements in the correct order, making decisions based on provider availability and experience.
        """,
        actions=[
            Action(name="reschedule_appointment", kwargs={"appointment_id": "APPT007", "new_date": "2025-01-22", "new_time": "15:00"}),
            Action(name="schedule_appointment", kwargs={"patient_id": "maria_rodriguez_4567", "provider_id": "dr_thompson_cardiology", "date": "2025-01-23", "time": "09:00", "appointment_type": "specialist_consultation"}),
        ],
        outputs=_task_three_outputs(),
    ),
    Task(
        annotator="3",
        user_id="maria_rodriguez_4567",
        instruction="""
        You are Maria Rodriguez, born December 3, 1990. Start by confirming your identity with your
        full name and date of birth. Retrieve your telehealth appointment history and locate the
        cardiology telehealth visit from Sunday, December 15, 2024 at 4:00 PM that still shows as
        pending approval and is now past due. Cancel that appointment before scheduling anything new.

        After the pending visit is cancelled, schedule a dermatologist follow-up with Dr. Lee on
        Tuesday, February 4, 2025 at 10:00 (10 AM) and ensure there are no conflicts. Once it is
        booked, double-check the appointment details and verify that the copay shown matches the
        specialist copay in your patient profile.
        """,
        actions=[
            Action(
                name="find_patient_by_name_dob",
                kwargs={"first_name": "Maria", "last_name": "Rodriguez", "date_of_birth": "1990-12-03"},
            ),
            Action(
                name="list_patient_appointments",
                kwargs={"patient_id": "maria_rodriguez_4567"},
            ),
            Action(
                name="cancel_appointment",
                kwargs={"appointment_id": "APPT009"},
            ),
            Action(
                name="schedule_appointment",
                kwargs={
                    "patient_id": "maria_rodriguez_4567",
                    "provider_id": "dr_lee_dermatology",
                    "date": "2025-02-04",
                    "time": "10:00",
                    "appointment_type": "follow_up",
                },
            ),
            Action(
                name="get_appointment_details",
                kwargs={"appointment_id": "APPT010"},
            ),
            Action(
                name="get_patient_details",
                kwargs={"patient_id": "maria_rodriguez_4567"},
            ),
        ],
        outputs=["45.00", "https://telehealth.healthcenter.com/room/APPT010"],
    ),
    Task(
        annotator="4",
        user_id="sarah_johnson_1234",
        instruction="""
        You are Sarah Johnson, email sarah.johnson@email.com. Authenticate yourself using your email.
        Review only your pending telehealth appointments to locate the cardiology consult that was set
        for Thursday, January 18, 2024 at 3:00 PM and is still waiting on approval. Cancel that pending
        appointment before making any schedule changes.

        Once the cardiology visit is cancelled, double-check Dr. Garcia's availability to make sure he
        has an 11:00 AM slot open on Monday, January 15, 2024. Move your routine primary-care visit
        (APPT001) on that day from 9:00 AM to 11:00 AM. After rescheduling, pull the updated appointment
        details so you can relay the meeting link, and confirm that the listed copay for the visit still
        matches the primary-care copay in your patient profile.
        """,
        actions=[
            Action(
                name="find_patient_by_email",
                kwargs={"email": "sarah.johnson@email.com"},
            ),
            Action(
                name="list_patient_appointments",
                kwargs={"patient_id": "sarah_johnson_1234", "status_filter": "pending_approval"},
            ),
            Action(
                name="cancel_appointment",
                kwargs={"appointment_id": "APPT004"},
            ),
            Action(
                name="get_provider_details",
                kwargs={"provider_id": "dr_garcia_primary"},
            ),
            Action(
                name="reschedule_appointment",
                kwargs={"appointment_id": "APPT001", "new_date": "2024-01-15", "new_time": "11:00"},
            ),
            Action(
                name="get_appointment_details",
                kwargs={"appointment_id": "APPT001"},
            ),
            Action(
                name="get_patient_details",
                kwargs={"patient_id": "sarah_johnson_1234"},
            ),
        ],
        outputs=["25.00", "https://telehealth.healthcenter.com/room/APPT001"],
    ),
    Task(
        annotator="5",
        user_id="emily_chen_9012",
        instruction="""
        You are Emily Chen, born July 8, 1992. Authenticate with your full name and date of birth. Review
        the medical record from your January 17, 2024 dermatology visit to confirm the treatment plan that
        was recommended. After verifying the plan, check Dr. Patel's availability for that same day and
        move your appointment (APPT003) from 11:00 AM to the earliest available afternoon slot.

        Once the appointment is rescheduled, retrieve the updated appointment details and confirm that the
        meeting link is still correct. Finally, reference your patient profile to make sure the copay listed
        for the visit aligns with your specialist copay.
        """,
        actions=[
            Action(
                name="find_patient_by_name_dob",
                kwargs={"first_name": "Emily", "last_name": "Chen", "date_of_birth": "1992-07-08"},
            ),
            Action(
                name="get_medical_record",
                kwargs={"record_id": "REC003"},
            ),
            Action(
                name="get_provider_details",
                kwargs={"provider_id": "dr_patel_dermatology"},
            ),
            Action(
                name="reschedule_appointment",
                kwargs={"appointment_id": "APPT003", "new_date": "2024-01-17", "new_time": "14:00"},
            ),
            Action(
                name="get_appointment_details",
                kwargs={"appointment_id": "APPT003"},
            ),
            Action(
                name="get_patient_details",
                kwargs={"patient_id": "emily_chen_9012"},
            ),
        ],
        outputs=["Hydrocortisone 1% cream", "40.00", "https://telehealth.healthcenter.com/room/APPT003"],
    ),
    Task(
        annotator="6",
        user_id="linda_parker_8899",
        instruction="""
        You are Linda Parker, email linda.parker@email.com. You need a cardiology telehealth slot the
        week of March 17, 2025, but your manager only releases you in the mornings unless nothing is
        available. Follow your tiered plan exactly and attempt each option in order, even if you think it
        will be unavailable. Stay focused on cardiology providers (Dr. Thompson and Dr. Smith):

        1. Try Dr. Thompson (the senior cardiologist) at 9:00 AM on Tuesday, March 18, 2025.
        2. If that slot is already taken, immediately check Dr. Smith for a 10:00 AM appointment the
           same morning.
        3. If neither morning works, abandon Tuesday and book a Thursday afternoon visit (after 1 PM)
           with whichever cardiologist has at least 20 years of experience.

        As you work through those options, sanity-check the providers' schedules and experience levels,
        and keep me updated on which branch you end up using. Once you lock something in, pull the
        appointment details and confirm that the meeting link (include at least the base URL) and
        specialist copay align with my
        profile. I also want to hear which cardiologist ultimately satisfied the 20+ year requirement.
        """,
        actions=[
            Action(
                name="find_patient_by_email",
                kwargs={"email": "linda.parker@email.com"},
            ),
            Action(
                name="get_provider_details",
                kwargs={"provider_id": "dr_thompson_cardiology"},
            ),
            Action(
                name="schedule_appointment",
                kwargs={
                    "patient_id": "linda_parker_8899",
                    "provider_id": "dr_thompson_cardiology",
                    "date": "2025-03-18",
                    "time": "09:00",
                    "appointment_type": "specialist_consultation",
                },
            ),
            Action(
                name="get_provider_details",
                kwargs={"provider_id": "dr_smith_cardiology"},
            ),
            Action(
                name="schedule_appointment",
                kwargs={
                    "patient_id": "linda_parker_8899",
                    "provider_id": "dr_smith_cardiology",
                    "date": "2025-03-18",
                    "time": "10:00",
                    "appointment_type": "specialist_consultation",
                },
            ),
            Action(
                name="list_available_providers",
                kwargs={"specialty": "Cardiology"},
            ),
            Action(
                name="schedule_appointment",
                kwargs={
                    "patient_id": "linda_parker_8899",
                    "provider_id": "dr_thompson_cardiology",
                    "date": "2025-03-20",
                    "time": "14:00",
                    "appointment_type": "specialist_consultation",
                },
            ),
            Action(
                name="get_appointment_details",
                kwargs={"appointment_id": "APPT013"},
            ),
            Action(
                name="get_patient_details",
                kwargs={"patient_id": "linda_parker_8899"},
            ),
        ],
        outputs=["Dr. Thompson", "55.00", "https://telehealth.healthcenter.com/room/"],
    ),
    Task(
        annotator="7",
        user_id="noah_ito_98187",
        instruction="""
        You are Noah Ito, born August 19, 1989, ZIP code 98187. You're impatient and give requests in
        pieces. Handle each step in order:

        1. Authenticate with your full name and date of birth.
        2. You just booked APPT014 (Dr. Garcia) and APPT015 (Dr. Smith). Without me repeating the address,
           peek at my patient profile so you remember the New York contact details before adjusting anything.
        3. Move APPT014 to the latest morning slot Dr. Garcia has on Tuesday, April 8, 2025 (no afternoons).
        4. Clean up APPT015 by canceling it, then try to grab Wednesday, April 9 at 10:00 AM with
           Dr. Thompson. If she is already taken, fall back to the first Thursday slot after 1:00 PM with a
           cardiologist who has at least 20 years of experience.
        5. Once the new cardiology appointment is confirmed, pull the appointment details and make sure the
           meeting link and specialist copay match what my insurance profile says. Also tell me explicitly
           which cardiologist satisfied the 20+ year requirement.
        """,
        actions=[
            Action(
                name="find_patient_by_name_dob",
                kwargs={"first_name": "Noah", "last_name": "Ito", "date_of_birth": "1989-08-19"},
            ),
            Action(
                name="list_patient_appointments",
                kwargs={"patient_id": "noah_ito_98187"},
            ),
            Action(
                name="get_patient_details",
                kwargs={"patient_id": "noah_ito_98187"},
            ),
            Action(
                name="reschedule_appointment",
                kwargs={"appointment_id": "APPT014", "new_date": "2025-04-08", "new_time": "11:00"},
            ),
            Action(
                name="cancel_appointment",
                kwargs={"appointment_id": "APPT015"},
            ),
            Action(
                name="get_provider_details",
                kwargs={"provider_id": "dr_thompson_cardiology"},
            ),
            Action(
                name="schedule_appointment",
                kwargs={
                    "patient_id": "noah_ito_98187",
                    "provider_id": "dr_thompson_cardiology",
                    "date": "2025-04-09",
                    "time": "10:00",
                    "appointment_type": "specialist_consultation",
                },
            ),
            Action(
                name="list_available_providers",
                kwargs={"specialty": "Cardiology"},
            ),
            Action(
                name="schedule_appointment",
                kwargs={
                    "patient_id": "noah_ito_98187",
                    "provider_id": "dr_thompson_cardiology",
                    "date": "2025-04-10",
                    "time": "14:00",
                    "appointment_type": "specialist_consultation",
                },
            ),
            Action(
                name="get_appointment_details",
                kwargs={"appointment_id": "APPT017"},
            ),
            Action(
                name="get_patient_details",
                kwargs={"patient_id": "noah_ito_98187"},
            ),
        ],
        outputs=["Dr. Thompson", "60.00", "https://telehealth.healthcenter.com/room/APPT017"],
    ),
    Task(
        annotator="9",
        user_id="olivia_martin_4433",
        instruction="""
        You are Olivia Martin, born February 11, 1994. You're juggling spring allergies, asthma tune-ups,
        and a pharmacist consult. Piece this together without missing the allergy warning:

        - Authenticate me via full name and DOB first.
        - I just pinged the portal asking for two refills: the rescue albuterol inhaler and that
          sulfamethoxazole course my coworker swears by. Before you promise anything, dig up my most
          recent virtual visit notes from late March (the ones Dr. Garcia wrote) and double-check the
          allergy section in my profile.
        - If the notes hint at any conflict, refuse the bad refill explicitly, but greenlight the safe one.
          I still want a concrete path forward, not just "no".
        - Then line up a telehealth pharmacist check-in with PharmD Jones on Thursday, April 3, 2025 at
          14:30 Pacific (she handles med coaching for our clinic). Make sure nothing else I have overlaps.
        - Once that's booked, send me the appointment specifics and quote the copay pulled straight from my
          insurance info. Remember: I only trust answers that connect the dots between the allergy warning,
          the approved refill, and the pharmacist session link.
        """,
        actions=[
            Action(
                name="find_patient_by_name_dob",
                kwargs={"first_name": "Olivia", "last_name": "Martin", "date_of_birth": "1994-02-11"},
            ),
            Action(
                name="get_medical_record",
                kwargs={"record_id": "REC004"},
            ),
            Action(
                name="get_patient_details",
                kwargs={"patient_id": "olivia_martin_4433"},
            ),
            Action(
                name="list_patient_appointments",
                kwargs={"patient_id": "olivia_martin_4433"},
            ),
            Action(
                name="schedule_appointment",
                kwargs={
                    "patient_id": "olivia_martin_4433",
                    "provider_id": "pharmacist_jones",
                    "date": "2025-04-03",
                    "time": "14:30",
                    "appointment_type": "consultation",
                },
            ),
            Action(
                name="get_appointment_details",
                kwargs={"appointment_id": "APPT019"},
            ),
        ],
        outputs=["sulfa allergy", "Albuterol", "https://telehealth.healthcenter.com/room/"],
    ),
    Task(
        annotator="9",
        user_id="maria_rodriguez_4567",
        instruction="""
        You are Maria Rodriguez (DOB 1990-12-03) catching up on that telehealth to-do list. The mid-December cardiology video visit with Dr. Smith (the one stamped APPT009 at 4 PM) never cleared insurance, so check with the assistant who you are, see whether that slot is still stuck in pending land, and only if it hasn’t been approved yet do you have them remove it so nothing lingers. Once that old booking is out of the way, you want a fresh specialist telehealth consult with whichever cardiologist has the deepest experience—start with Dr. Margaret Thompson—and you only want it if she can take you exactly at 09:00 on Tuesday, January 23, 2025. If she can’t or that time is gone, fall back to Dr. Robert Smith at that same moment; if neither doctor can commit to 09:00, you leave everything canceled and just report back. No matter how it ends, you expect to hear the insurance copay and see the telehealth link for whatever appointment winds up surviving. Keep the tone polite but brisk and expect the assistant to double-check availability instead of guessing.
        """,
        actions=[
            Action(name="find_patient_by_name_dob", kwargs={"first_name": "Maria", "last_name": "Rodriguez", "date_of_birth": "1990-12-03"}),
            Action(name="list_patient_appointments", kwargs={"patient_id": "maria_rodriguez_4567", "status_filter": "pending_approval"}),
            Action(name="cancel_appointment", kwargs={"appointment_id": "APPT009"}),
            Action(name="list_available_providers", kwargs={"specialty": "Cardiology"}),
            Action(name="get_provider_details", kwargs={"provider_id": "dr_thompson_cardiology"}),
            Action(name="schedule_appointment", kwargs={"patient_id": "maria_rodriguez_4567", "provider_id": "dr_thompson_cardiology", "date": "2025-01-23", "time": "09:00", "appointment_type": "specialist_consultation"}),
            Action(name="get_patient_details", kwargs={"patient_id": "maria_rodriguez_4567"}),
        ],
        outputs=_task_nine_outputs(),
    ),
    Task(
        annotator="10",
        user_id="daiki_sanchez_46236",
        instruction="""
        You are Daiki Sanchez (DOB 1991-05-27) checking the portal yet again. You already fired off a note earlier asking whether that cardiology telehealth consult you vaguely remember booking ever existed, so when the assistant finally answers you expect them to look you up by your portal email and sweep specifically for any cardiology visits still stuck in pending approval. If there is nothing waiting, fine—just say so and move on, but absolutely do not fabricate or auto-create a replacement without clearing it with you.

        Once that audit is done, you want to arrange a brand-new telehealth cardiology slot on Monday, April 14, 2025 at exactly 09:00, but you will only show up if the cardiologist both speaks Japanese and has at least 20 years of experience. You need those two traits together because your dad will be listening in. If even one of those requirements fails, you would rather be routed to a human scheduler and wait than settle for an English-only or junior doctor.

        You are curt, you do not let them bargain you into compromises, and if no provider satisfies both traits simultaneously you insist on being handed off to a person instead of letting them guess.
                """,
        actions=[
            Action(name="find_patient_by_email", kwargs={"email": "daikisanchez1479@example.com"}),
            Action(name="list_patient_appointments", kwargs={"patient_id": "daiki_sanchez_46236", "status_filter": "pending_approval"}),
            Action(name="list_available_providers", kwargs={"specialty": "Cardiology"}),
            Action(name="get_provider_details", kwargs={"provider_id": "dr_thompson_cardiology"}),
            Action(name="get_provider_details", kwargs={"provider_id": "dr_smith_cardiology"}),
            Action(name="transfer_to_human_support", kwargs={"reason": "No cardiologist meets the Japanese language plus 20-year experience requirement for the requested slot"}),
        ],
        outputs=[],
    ),
    Task(
        annotator="11",
        user_id="heather_collins_48201",
        instruction="""
        You are Heather Collins, born April 19, 1982, dialing in from Grand Rapids. The email on your portal is heather.collins82@gmail.com. You want a straight answer: the prescriptions from your last four telehealth encounters and, for each, the cheapest Indian supplier the hospital catalog lists—company, brand, price in USD for the medications in those prescriptions. If a drug has no Indian supplier, you expect to be told that plainly. You’re terse, impatient, and not interested in explanations.
        """,
        actions=[
            Action(name="find_patient_by_email", kwargs={"email": "heather.collins82@gmail.com"}),
            Action(name="list_patient_medical_records", kwargs={"patient_id": "heather_collins_48201", "limit": 4}),
            Action(name="get_medical_record", kwargs={"record_id": "REC008"}),
            Action(name="get_medical_record", kwargs={"record_id": "REC007"}),
            Action(name="get_medical_record", kwargs={"record_id": "REC006"}),
            Action(name="get_medical_record", kwargs={"record_id": "REC005"}),
            Action(name="list_medication_suppliers", kwargs={"medication": "Sertraline", "country_filter": "India"}),
            Action(name="list_medication_suppliers", kwargs={"medication": "Buspirone", "country_filter": "India"}),
            Action(name="list_medication_suppliers", kwargs={"medication": "Montelukast", "country_filter": "India"}),
            Action(name="list_medication_suppliers", kwargs={"medication": "Fluticasone Inhaler", "country_filter": "India"}),
            Action(name="list_medication_suppliers", kwargs={"medication": "Metoprolol Succinate", "country_filter": "India"}),
            Action(name="list_medication_suppliers", kwargs={"medication": "Aspirin EC", "country_filter": "India"}),
            Action(name="list_medication_suppliers", kwargs={"medication": "Atorvastatin", "country_filter": "India"}),
        ],
        outputs=_task_eleven_outputs(),
    ),
]

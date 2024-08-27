import telebot
import spacy
import json
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

API_TOKEN = 'BOT TOKEN'

bot = telebot.TeleBot(API_TOKEN)
nlp = spacy.load('en_core_web_md')

# Dictionary to store user profiles
user_profiles = {}

# Scheduler for reminders
scheduler = BackgroundScheduler()
scheduler.start()

# Symptom to recommendation and causes mapping (with external links)
recommendations_and_causes = {
    "headache": {
        "description": "A headache is a pain or discomfort in the head, scalp, or neck.",
        "cause": "Possible causes include stress, dehydration, poor posture, or eye strain.",
        "prevention": "Drink plenty of water, maintain good posture, and avoid long periods of screen time.",
        "home_remedies": "Drink water, rest in a quiet, dark room, and apply a cold compress to your forehead.",
        "medication": "Over-the-counter pain relievers such as ibuprofen or acetaminophen.",
        "link": "https://www.apollo247.com/disease/headache"
    },
    "fever": {
        "description": "A fever is a temporary increase in your body temperature, often due to an illness.",
        "cause": "Fever is usually caused by an infection, such as a cold or flu, or inflammation.",
        "prevention": "Practice good hygiene, get vaccinated, and avoid contact with sick individuals.",
        "home_remedies": "Stay hydrated, rest, and apply a cool, damp cloth to your forehead.",
        "medication": "Antipyretics such as acetaminophen or ibuprofen.",
        "link": "https://www.betterhealth.vic.gov.au/health/conditionsandtreatments/fever"
    },
    "cough": {
        "description": "A cough is a reflex action to clear your airways of mucus and irritants.",
        "cause": "Common causes include respiratory infections, allergies, or irritants like smoke.",
        "prevention": "Avoid smoking, stay away from pollutants, and wash your hands frequently.",
        "home_remedies": "Drink warm fluids, use a humidifier, and take honey for throat soothing.",
        "medication": "Over-the-counter cough medicines and expectorants.",
        "link": "https://www.apollo247.com/disease/cough"
    },
    "sorethroat": {
        "description": "A sore throat is a painful, dry, or scratchy feeling in the throat.",
        "cause": "A sore throat can be caused by viral infections, bacterial infections, or environmental factors.",
        "prevention": "Avoid close contact with sick people, don't smoke, and stay hydrated.",
        "home_remedies": "Gargle with salt water, drink warm liquids, and use throat lozenges.",
        "medication": "Pain relievers like ibuprofen or acetaminophen, and throat sprays.",
        "link": "https://www.apollo247.com/disease/sore-throat"
    },
    "stomach ache": {
        "description": "A stomach ache is pain that occurs between the chest and pelvic regions.",
        "cause": "Possible causes include indigestion, gas, infection, or stress.",
        "prevention": "Eat smaller meals, avoid spicy and fatty foods, and manage stress.",
        "home_remedies": "Sip water or clear fluids, avoid solid food for a few hours, and try ginger tea.",
        "medication": "Antacids, anti-gas medications, or antispasmodics.",
        "link": "https://www.apollo247.com/disease/stomach-pain"
    },
    "back pain": {
        "description": "Back pain is a common ailment that can range from a dull, constant ache to a sudden, sharp pain.",
        "cause": "Possible causes include muscle or ligament strain, bulging or ruptured discs, arthritis, or skeletal irregularities.",
        "prevention": "Maintain a healthy weight, exercise regularly, and practice good posture.",
        "home_remedies": "Rest, apply ice or heat, and use over-the-counter pain relievers.",
        "medication": "NSAIDs like ibuprofen or naproxen, muscle relaxants, or topical pain relievers.",
        "link": "https://www.mayoclinic.org/diseases-conditions/back-pain/symptoms-causes/syc-20369906"
    },
    "nausea": {
        "description": "Nausea is a feeling of sickness with an inclination to vomit.",
        "cause": "Possible causes include motion sickness, migraines, medication side effects, or gastrointestinal issues.",
        "prevention": "Avoid strong odors, eat small meals, and stay hydrated.",
        "home_remedies": "Sip ginger tea, eat bland foods like crackers, and avoid greasy or spicy foods.",
        "medication": "Antiemetics like ondansetron or metoclopramide.",
        "link": "https://www.webmd.com/digestive-disorders/understanding-nausea-vomiting-treatment"
    },
    "fatigue": {
        "description": "Fatigue is a feeling of extreme tiredness and lack of energy.",
        "cause": "Possible causes include lack of sleep, poor diet, stress, or underlying medical conditions.",
        "prevention": "Get adequate sleep, eat a balanced diet, and manage stress effectively.",
        "home_remedies": "Take short naps, avoid caffeine and alcohol before bedtime, and exercise regularly.",
        "medication": "Depending on the underlying cause, treatments may vary. Consult a healthcare provider for appropriate options.",
        "link": "https://www.healthline.com/health/fatigue"
    },
    "rash": {
        "description": "A rash is an area of irritated or swollen skin.",
        "cause": "Possible causes include allergies, infections, heat, or irritants.",
        "prevention": "Avoid known allergens, maintain good hygiene, and stay cool and dry.",
        "home_remedies": "Apply moisturizers, avoid scratching, and use over-the-counter hydrocortisone cream.",
        "medication": "Antihistamines for allergic reactions, topical steroids, or antifungal creams.",
        "link": "https://www.webmd.com/skin-problems-and-treatments/guide/rash"
    },
    "dizziness": {
        "description": "Dizziness is a term used to describe a range of sensations, such as feeling faint, woozy, weak, or unsteady.",
        "cause": "Possible causes include dehydration, inner ear problems, medication side effects, or low blood sugar.",
        "prevention": "Stay hydrated, avoid sudden movements, and eat regular meals.",
        "home_remedies": "Sit or lie down until the dizziness passes, drink water, and avoid bright lights.",
        "medication": "Meclizine for motion sickness, or medications to treat the underlying cause.",
        "link": "https://www.mayoclinic.org/symptoms/dizziness/basics/definition/sym-20050729"
    },
    "anxiety": {
        "description": "Anxiety is a feeling of worry, nervousness, or unease about something with an uncertain outcome.",
        "cause": "Possible causes include stress, genetics, brain chemistry, or traumatic events.",
        "prevention": "Manage stress through relaxation techniques, exercise, and adequate sleep.",
        "home_remedies": "Practice deep breathing, meditate, and stay active.",
        "medication": "Anti-anxiety medications like benzodiazepines or antidepressants.",
        "link": "https://www.apa.org/topics/anxiety"
    },
    "constipation": {
        "description": "Constipation is infrequent bowel movements or difficulty passing stools.",
        "cause": "Possible causes include a low-fiber diet, dehydration, lack of exercise, or certain medications.",
        "prevention": "Eat a high-fiber diet, drink plenty of water, and exercise regularly.",
        "home_remedies": "Eat prunes or bran cereal, stay hydrated, and avoid processed foods.",
        "medication": "Laxatives, stool softeners, or fiber supplements.",
        "link": "https://www.webmd.com/digestive-disorders/understanding-constipation-treatment"
    },
    "diarrhea": {
        "description": "Diarrhea is loose, watery stools that occur more frequently than usual.",
        "cause": "Possible causes include infections, food intolerance, medications, or digestive disorders.",
        "prevention": "Maintain good hygiene, avoid questionable foods and water, and manage stress.",
        "home_remedies": "Stay hydrated, eat bland foods like bananas and rice, and avoid dairy products.",
        "medication": "Anti-diarrheal medications like loperamide or bismuth subsalicylate.",
        "link": "https://www.mayoclinic.org/diseases-conditions/diarrhea/symptoms-causes/syc-20352210"
    },
    "insomnia": {
        "description": "Insomnia is difficulty falling asleep or staying asleep.",
        "cause": "Possible causes include stress, anxiety, medications, or sleep disorders.",
        "prevention": "Maintain a regular sleep schedule, avoid caffeine and electronics before bed.",
        "home_remedies": "Practice relaxation techniques, create a comfortable sleep environment.",
        "medication": "Sleep aids like melatonin or prescription medications.",
        "link": "https://www.sleepfoundation.org/insomnia"
    },
    "heartburn": {
        "description": "Heartburn is a burning sensation in the chest, often after eating, that might worsen at night.",
        "cause": "Possible causes include acid reflux, overeating, or eating certain foods.",
        "prevention": "Avoid spicy and fatty foods, eat smaller meals, and don't lie down after eating.",
        "home_remedies": "Drink water, eat a banana, or chew gum.",
        "medication": "Antacids, H2 blockers, or proton pump inhibitors.",
        "link": "https://www.webmd.com/heartburn-gerd/guide/heartburn-gerd-treatment-overview"
    },
    "allergies": {
        "description": "Allergies are immune system reactions to substances that are usually not harmful.",
        "cause": "Possible causes include pollen, dust, pet dander, or certain foods.",
        "prevention": "Avoid known allergens, keep windows closed during high pollen seasons.",
        "home_remedies": "Use saline nasal sprays, take showers after being outside, and use air purifiers.",
        "medication": "Antihistamines, decongestants, or corticosteroids.",
        "link": "https://www.webmd.com/allergies/guide/allergy-relief"
    },
    "cold": {
        "description": "The common cold is a viral infection of your nose and throat (upper respiratory tract).",
        "cause": "Caused by various viruses, most commonly rhinoviruses.",
        "prevention": "Wash hands frequently, avoid close contact with sick people.",
        "home_remedies": "Rest, stay hydrated, and use saline nasal drops.",
        "medication": "Decongestants, pain relievers, and cough syrups.",
        "link": "https://www.mayoclinic.org/diseases-conditions/common-cold/symptoms-causes/syc-20351605"
    },
    "flu": {
        "description": "Flu is a viral infection that attacks your respiratory system — your nose, throat, and lungs.",
        "cause": "Caused by influenza viruses.",
        "prevention": "Get vaccinated annually, wash hands frequently, and avoid close contact with sick people.",
        "home_remedies": "Rest, stay hydrated, and use over-the-counter medications to relieve symptoms.",
        "medication": "Antiviral drugs and over-the-counter medications.",
        "link": "https://www.cdc.gov/flu/symptoms/treatment.htm"
    },
    "migraine": {
        "description": "A migraine is a headache that can cause severe throbbing pain or a pulsing sensation, usually on one side of the head.",
        "cause": "Possible causes include genetics, hormonal changes, or certain triggers like stress or certain foods.",
        "prevention": "Identify and avoid triggers, maintain a regular sleep schedule, and manage stress.",
        "home_remedies": "Rest in a dark, quiet room, apply cold compresses, and stay hydrated.",
        "medication": "Pain relievers, triptans, or anti-nausea medications.",
        "link": "https://www.webmd.com/migraines-headaches/guide/migraine-treatment-overview"
    },
    "sneezing": {
        "description": "Sneezing is a sudden, forceful, uncontrolled burst of air through the nose and mouth.",
        "cause": "Possible causes include allergies, infections, or irritants like dust or smoke.",
        "prevention": "Avoid known allergens and irritants, maintain good hygiene.",
        "home_remedies": "Use saline nasal spray, stay hydrated, and avoid exposure to irritants.",
        "medication": "Antihistamines for allergies or decongestants.",
        "link": "https://www.webmd.com/allergies/ss/slideshow-allergies-overview"
    },
    "itching": {
        "description": "Itching is an irritating sensation that makes you want to scratch your skin.",
        "cause": "Possible causes include dry skin, allergies, or skin conditions like eczema.",
        "prevention": "Moisturize regularly, avoid known allergens, and use mild soaps.",
        "home_remedies": "Apply moisturizers, use cool compresses, and avoid scratching.",
        "medication": "Antihistamines, topical steroids, or moisturizers.",
        "link": "https://www.mayoclinic.org/symptoms/itching/basics/definition/sym-20050925"
    },
    "vomiting": {
        "description": "Vomiting is the involuntary, forceful expulsion of the contents of one's stomach through the mouth.",
        "cause": "Possible causes include infections, food poisoning, motion sickness, or pregnancy.",
        "prevention": "Avoid known triggers, eat small meals, and stay hydrated.",
        "home_remedies": "Sip clear fluids, eat bland foods, and rest.",
        "medication": "Antiemetics like ondansetron or metoclopramide.",
        "link": "https://www.webmd.com/digestive-disorders/understanding-nausea-vomiting-treatment"
    },
    "blurred vision": {
        "description": "Blurred vision is the lack of sharpness of vision, resulting in the inability to see fine details.",
        "cause": "Possible causes include refractive errors, cataracts, or diabetes.",
        "prevention": "Regular eye exams, control blood sugar levels, and wear protective eyewear.",
        "home_remedies": "Rest your eyes, use artificial tears, and improve lighting.",
        "medication": "Eyeglasses, contact lenses, or medications to treat underlying conditions.",
        "link": "https://www.webmd.com/eye-health/ss/slideshow-blurred-vision-causes"
    },
    "chest pain": {
        "description": "Chest pain is any pain that occurs in the chest area.",
        "cause": "Possible causes include heart-related issues, lung problems, or gastrointestinal issues.",
        "prevention": "Maintain a healthy lifestyle, avoid smoking, and manage stress.",
        "home_remedies": "Rest, avoid heavy meals, and stay hydrated.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.mayoclinic.org/symptoms/chest-pain/basics/definition/sym-20050838"
    },
    "shortness of breath": {
        "description": "Shortness of breath is a feeling of not being able to breathe well enough.",
        "cause": "Possible causes include asthma, heart conditions, or respiratory infections.",
        "prevention": "Avoid smoking, maintain a healthy weight, and exercise regularly.",
        "home_remedies": "Pursed-lip breathing, sit forward in a chair, and stay calm.",
        "medication": "Inhalers for asthma, medications for heart conditions, or antibiotics for infections.",
        "link": "https://www.webmd.com/asthma/ss/slideshow-shortness-of-breath"
    },
    "chills": {
        "description": "Chills are feelings of coldness accompanied by shivering.",
        "cause": "Possible causes include infections, cold exposure, or low blood sugar.",
        "prevention": "Dress warmly, avoid exposure to cold, and maintain good hygiene.",
        "home_remedies": "Stay warm, drink warm fluids, and rest.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.healthline.com/symptom/chills"
    },
    "muscle pain": {
        "description": "Muscle pain is an aching or discomfort in the muscles.",
        "cause": "Possible causes include overuse, injury, or infections.",
        "prevention": "Warm up before exercise, maintain proper posture, and stay hydrated.",
        "home_remedies": "Rest, apply ice or heat, and stretch.",
        "medication": "NSAIDs like ibuprofen or acetaminophen.",
        "link": "https://www.webmd.com/pain-management/guide/muscle-pain-causes-treatments"
    },
    "joint pain": {
        "description": "Joint pain is discomfort, aches, and soreness in any of the body's joints.",
        "cause": "Possible causes include arthritis, injury, or overuse.",
        "prevention": "Maintain a healthy weight, exercise regularly, and avoid repetitive stress on joints.",
        "home_remedies": "Rest, apply ice or heat, and perform gentle stretching exercises.",
        "medication": "NSAIDs like ibuprofen, corticosteroids, or disease-modifying antirheumatic drugs (DMARDs).",
        "link": "https://www.webmd.com/pain-management/guide/joint-pain-causes"
    },
    "ear pain": {
        "description": "Ear pain is a sharp, dull, or burning pain in one or both ears.",
        "cause": "Possible causes include infections, earwax buildup, or changes in air pressure.",
        "prevention": "Avoid inserting objects into the ear, maintain good hygiene, and manage allergies.",
        "home_remedies": "Apply a warm compress, use over-the-counter ear drops, and rest.",
        "medication": "Pain relievers like ibuprofen, antibiotics for infections, or ear drops.",
        "link": "https://www.webmd.com/cold-and-flu/ear-infection/understanding-ear-infections-treatment"
    },
    "nosebleed": {
        "description": "A nosebleed is the loss of blood from the tissue lining the inside of your nose.",
        "cause": "Possible causes include dry air, trauma, or underlying health conditions.",
        "prevention": "Use a humidifier, avoid picking your nose, and stay hydrated.",
        "home_remedies": "Pinch your nose, lean forward, and apply a cold compress.",
        "medication": "Nasal sprays to moisturize, or cauterization for frequent nosebleeds.",
        "link": "https://www.webmd.com/first-aid/nosebleeds-treatment"
    },
    "runny nose": {
        "description": "A runny nose is excess drainage produced by nasal and adjacent tissues and blood vessels in the nose.",
        "cause": "Possible causes include infections, allergies, or irritants.",
        "prevention": "Avoid known allergens and irritants, maintain good hygiene.",
        "home_remedies": "Stay hydrated, use saline nasal sprays, and rest.",
        "medication": "Decongestants, antihistamines, or nasal sprays.",
        "link": "https://www.webmd.com/cold-and-flu/why-is-my-nose-always-running"
    },
    "bloating": {
        "description": "Bloating is a feeling of fullness or swelling in the abdomen.",
        "cause": "Possible causes include overeating, gas, or digestive disorders.",
        "prevention": "Eat smaller meals, avoid carbonated drinks, and manage stress.",
        "home_remedies": "Drink peppermint tea, avoid foods that cause gas, and stay active.",
        "medication": "Antacids, simethicone, or probiotics.",
        "link": "https://www.webmd.com/ibs/guide/abdominal-bloating"
    },
    "sweating": {
        "description": "Sweating is the body's way of regulating temperature by releasing water and salt.",
        "cause": "Possible causes include exercise, heat, stress, or medical conditions.",
        "prevention": "Stay cool, avoid triggers, and practice good hygiene.",
        "home_remedies": "Stay hydrated, wear breathable clothing, and use antiperspirants.",
        "medication": "Antiperspirants, prescription medications, or botox injections.",
        "link": "https://www.mayoclinic.org/symptoms/excessive-sweating/basics/definition/sym-20050780"
    },
    "swelling": {
        "description": "Swelling is an increase in the size or a change in the shape of an area of the body.",
        "cause": "Possible causes include injury, infection, or underlying medical conditions.",
        "prevention": "Avoid injury, maintain good hygiene, and manage chronic conditions.",
        "home_remedies": "Rest, elevate the affected area, and apply ice.",
        "medication": "NSAIDs like ibuprofen or medications to treat the underlying cause.",
        "link": "https://www.webmd.com/skin-problems-and-treatments/ss/slideshow-skin-sos"
    },
    "bruising": {
        "description": "Bruising occurs when small blood vessels break and leak blood under the skin.",
        "cause": "Possible causes include injury, certain medications, or medical conditions.",
        "prevention": "Avoid injury, wear protective gear, and be aware of medication side effects.",
        "home_remedies": "Apply ice, elevate the affected area, and rest.",
        "medication": "Pain relievers like acetaminophen or NSAIDs.",
        "link": "https://www.webmd.com/first-aid/bruises-treatment"
    },
    "tingling": {
        "description": "Tingling is a sensation of pins and needles often felt in the hands, feet, arms, or legs.",
        "cause": "Possible causes include nerve compression, poor circulation, or medical conditions like diabetes.",
        "prevention": "Maintain good posture, avoid repetitive stress, and manage chronic conditions.",
        "home_remedies": "Move around to improve circulation, avoid tight clothing, and practice good ergonomics.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.mayoclinic.org/symptoms/numbness/basics/definition/sym-20050938"
    },
    "cramps": {
        "description": "Cramps are sudden, involuntary muscle contractions or spasms.",
        "cause": "Possible causes include dehydration, overuse, or electrolyte imbalances.",
        "prevention": "Stay hydrated, stretch before exercise, and maintain a balanced diet.",
        "home_remedies": "Gently stretch and massage the muscle, apply heat or cold.",
        "medication": "Pain relievers like ibuprofen or acetaminophen.",
        "link": "https://www.webmd.com/pain-management/guide/muscle-cramps-causes-treatments"
    },
    "hair loss": {
        "description": "Hair loss is the gradual loss of hair from the scalp or body.",
        "cause": "Possible causes include genetics, hormonal changes, or medical conditions.",
        "prevention": "Avoid harsh hair treatments, maintain a healthy diet, and manage stress.",
        "home_remedies": "Use gentle hair care products, massage the scalp, and try essential oils.",
        "medication": "Minoxidil, finasteride, or other treatments as advised by a healthcare provider.",
        "link": "https://www.mayoclinic.org/diseases-conditions/hair-loss/diagnosis-treatment/drc-20372932"
    },
    "weight gain": {
        "description": "Weight gain is an increase in body weight.",
        "cause": "Possible causes include overeating, lack of exercise, or medical conditions.",
        "prevention": "Maintain a balanced diet, exercise regularly, and monitor weight.",
        "home_remedies": "Eat a balanced diet, increase physical activity, and track calorie intake.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.webmd.com/diet/ss/slideshow-weight-gain-shockers"
    },
    "weight loss": {
        "description": "Weight loss is a decrease in body weight.",
        "cause": "Possible causes include diet, exercise, or medical conditions.",
        "prevention": "Maintain a balanced diet, exercise regularly, and monitor weight.",
        "home_remedies": "Eat nutrient-dense foods, avoid skipping meals, and consult a nutritionist.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.mayoclinic.org/symptoms/unexplained-weight-loss/basics/definition/sym-20050700"
    },
    "high blood pressure": {
        "description": "High blood pressure is a condition in which the force of the blood against the artery walls is too high.",
        "cause": "Possible causes include genetics, poor diet, lack of exercise, or stress.",
        "prevention": "Maintain a healthy diet, exercise regularly, and manage stress.",
        "home_remedies": "Reduce salt intake, stay active, and maintain a healthy weight.",
        "medication": "Antihypertensive medications as prescribed by a healthcare provider.",
        "link": "https://www.mayoclinic.org/diseases-conditions/high-blood-pressure/symptoms-causes/syc-20373410"
    },
    "low blood pressure": {
        "description": "Low blood pressure is a condition in which the blood pressure is lower than normal.",
        "cause": "Possible causes include dehydration, heart problems, or endocrine disorders.",
        "prevention": "Stay hydrated, avoid prolonged standing, and eat small, frequent meals.",
        "home_remedies": "Drink plenty of fluids, eat a balanced diet, and wear compression stockings.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.webmd.com/heart/understanding-low-blood-pressure-basics"
    },
    "depression": {
        "description": "Depression is a mood disorder that causes a persistent feeling of sadness and loss of interest.",
        "cause": "Possible causes include genetics, brain chemistry, or traumatic events.",
        "prevention": "Maintain a healthy lifestyle, stay connected with loved ones, and manage stress.",
        "home_remedies": "Exercise regularly, practice mindfulness, and engage in enjoyable activities.",
        "medication": "Antidepressants and psychotherapy.",
        "link": "https://www.mayoclinic.org/diseases-conditions/depression/symptoms-causes/syc-20356007"
    },
    "irritability": {
        "description": "Irritability is a feeling of agitation that can range from mild annoyance to intense frustration.",
        "cause": "Possible causes include stress, lack of sleep, or hormonal changes.",
        "prevention": "Manage stress, get adequate sleep, and maintain a balanced diet.",
        "home_remedies": "Practice relaxation techniques, exercise regularly, and ensure sufficient rest.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.webmd.com/mental-health/ss/slideshow-irritability"
    },
    "hot flashes": {
        "description": "Hot flashes are sudden feelings of warmth, often most intense over the face, neck, and chest.",
        "cause": "Possible causes include menopause, certain medications, or hormonal imbalances.",
        "prevention": "Maintain a healthy weight, avoid triggers like spicy foods, and stay cool.",
        "home_remedies": "Dress in layers, use a fan, and avoid caffeine and alcohol.",
        "medication": "Hormone therapy or other medications as advised by a healthcare provider.",
        "link": "https://www.mayoclinic.org/diseases-conditions/hot-flashes/symptoms-causes/syc-20352790"
    },
    "dry mouth": {
        "description": "Dry mouth is a condition in which the salivary glands in your mouth don't make enough saliva to keep your mouth wet.",
        "cause": "Possible causes include medications, dehydration, or certain medical conditions.",
        "prevention": "Stay hydrated, avoid tobacco, and use a humidifier.",
        "home_remedies": "Sip water regularly, chew sugar-free gum, and avoid caffeine and alcohol.",
        "medication": "Saliva substitutes or medications to stimulate saliva production.",
        "link": "https://www.mayoclinic.org/diseases-conditions/dry-mouth/symptoms-causes/syc-20356048"
    },
    "loss of appetite": {
        "description": "Loss of appetite is a decreased desire to eat.",
        "cause": "Possible causes include infections, chronic illnesses, or emotional stress.",
        "prevention": "Maintain a balanced diet, manage stress, and ensure regular physical activity.",
        "home_remedies": "Eat small, frequent meals, include nutrient-dense foods, and stay hydrated.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.webmd.com/digestive-disorders/ss/slideshow-loss-of-appetite"
    },
    "cough": {
        "description": "A cough is a sudden, forceful hacking sound to release air and clear irritation in the throat or airway.",
        "cause": "Possible causes include infections, allergies, or irritants like smoke.",
        "prevention": "Avoid known irritants, practice good hygiene, and stay hydrated.",
        "home_remedies": "Honey, warm liquids, and throat lozenges.",
        "medication": "Cough suppressants, expectorants, or antihistamines.",
        "link": "https://www.webmd.com/cold-and-flu/cough-suppressants"
    },
    "eye redness": {
        "description": "Eye redness, or red eye, can be caused by a variety of conditions.",
        "cause": "Possible causes include allergies, conjunctivitis, dry eyes, contact lens wear, eye strain, blepharitis, injury, uveitis, or glaucoma.",
        "prevention": "Avoid allergens, maintain good hygiene, follow proper contact lens care, take breaks during screen use, use humidifiers, and wear protective eyewear.",
        "home_remedies": "Apply a cold compress, use artificial tears, and avoid irritants.",
        "medication": "Antihistamine eye drops for allergies, antibiotic eye drops or ointments for bacterial conjunctivitis, and anti-inflammatory eye drops for conditions like uveitis or severe irritation.",
        "link": "https://www.mayoclinic.org/symptoms/red-eye/basics/definition/sym-20050748"
    },
    "dementia": {
        "description": "Dementia is a general term for a decline in mental ability severe enough to interfere with daily life.",
        "cause": "Causes include Alzheimer's disease, vascular dementia, Lewy body dementia, and frontotemporal dementia.",
        "prevention": "Stay mentally and socially active, maintain a healthy diet and regular physical activity, and control cardiovascular risk factors.",
        "home_remedies": "Engage in cognitive stimulation activities like puzzles and games, maintain a regular routine, and ensure a safe environment.",
        "medication": "Medications like cholinesterase inhibitors and memantine can help manage symptoms.",
        "link": "https://www.alz.org/alzheimers-dementia/what-is-dementia"
    },
    "hoarseness": {
        "description": "Hoarseness is a condition in which your voice sounds raspy, strained, or softer than usual.",
        "cause": "Possible causes include vocal strain, infections, or irritants like smoke.",
        "prevention": "Avoid shouting, stay hydrated, and use a humidifier.",
        "home_remedies": "Rest your voice, drink warm fluids, and avoid irritants.",
        "medication": "Depends on the underlying cause; consult a healthcare provider.",
        "link": "https://www.webmd.com/oral-health/hoarseness-treatment"
    }
}

# Helper function to delete webhook
def delete_webhook():
    current_webhook = bot.get_webhook_info()
    if current_webhook.url:
        bot.remove_webhook()

# Function to get or create user profile
def get_user_profile(user_id):
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            'name': None,
            'medical_history': [],
            'medications': [],
            'allergies': [],
            'symptoms': []
        }
    return user_profiles[user_id]

# Function to delete user profile
def delete_user_profile(user_id):
    if user_id in user_profiles:
        del user_profiles[user_id]
        save_profiles()  # Save the updated profiles to the JSON file
        return True
    else:
        return False

# Save user profiles to a file
def save_profiles():
    with open('user_profiles.json', 'w') as f:
        json.dump(user_profiles, f, indent=4)

# Load user profiles from a file
def load_profiles():
    global user_profiles
    try:
        with open('user_profiles.json', 'r') as f:
            user_profiles = json.load(f)
    except FileNotFoundError:
        user_profiles = {}

# Command handler to start setting up profile
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Hey there, Welcome to Medicare! Your personal health companion. \nLet's start by creating your profile.\nPlease enter your name.")
    print(f"[{datetime.now()}] User {message.chat.id} started interaction")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_profile = get_user_profile(message.chat.id)
    user_profile['name'] = message.text
    bot.send_message(message.chat.id, f"Great to meet you, {user_profile['name']}! Do you have any pre-existing conditions? Please list them separated by commas, or type 'none' if you have none.")
    print(f"[{datetime.now()}] User {message.chat.id} set name: {message.text}")
    bot.register_next_step_handler(message, get_medical_history)

def get_medical_history(message):
    user_profile = get_user_profile(message.chat.id)
    user_profile['medical_history'] = message.text.split(", ")
    bot.send_message(message.chat.id, "Now, please enter your current medications. List them separated by commas, or type 'none' if you're not taking any.")
    print(f"[{datetime.now()}] User {message.chat.id} set medical history: {message.text}")
    bot.register_next_step_handler(message, get_medications)

def get_medications(message):
    user_profile = get_user_profile(message.chat.id)
    user_profile['medications'] = message.text.split(", ")
    bot.send_message(message.chat.id, "Please enter any allergies you have.Type none if you don't have any.")
    print(f"[{datetime.now()}] User {message.chat.id} set medications: {message.text}")
    bot.register_next_step_handler(message, get_allergies)

def get_allergies(message):
    user_profile = get_user_profile(message.chat.id)
    user_profile['allergies'] = message.text.split(", ")
    save_profiles()  # Save the updated profiles to the JSON file
    bot.send_message(message.chat.id, "Thank you for providing your details! How can I assist you today? please describe your symptoms.")
    print(f"[{datetime.now()}] User {message.chat.id} set allergies: {message.text}")

# Function to set medication reminders
@bot.message_handler(commands=['remind'])
def set_reminder(message):
    bot.send_message(message.chat.id, "Please enter the medication name and reminder time (HH:MM) in 24-hour format.")
    print(f"[{datetime.now()}] User {message.chat.id} requested to set a reminder")
    bot.register_next_step_handler(message, get_reminder_details)

def get_reminder_details(message):
    try:
        details = message.text.split()
        medication = details[0]
        reminder_time = datetime.strptime(details[1], "%H:%M").time()
        user_profile = get_user_profile(message.chat.id)

        def send_reminder():
            bot.send_message(message.chat.id, f"Reminder: It's time to take your medication - {medication}")
            print(f"[{datetime.now()}] Reminder sent to user {message.chat.id} for medication: {medication}")

        reminder_datetime = datetime.combine(datetime.now().date(), reminder_time)
        if reminder_datetime < datetime.now():
            reminder_datetime += timedelta(days=1)

        scheduler.add_job(send_reminder, 'date', run_date=reminder_datetime)
        bot.send_message(message.chat.id, f"Reminder set for {medication} at {reminder_time.strftime('%H:%M')} every day.")
        print(f"[{datetime.now()}] Reminder set for user {message.chat.id} for medication: {medication} at {reminder_time.strftime('%H:%M')}")
    except Exception as e:
        bot.send_message(message.chat.id, "Sorry, I couldn't understand the details. Please use the format: medication_name HH:MM.")
        print(f"[{datetime.now()}] Failed to set reminder for user {message.chat.id} due to error: {str(e)}")

# Handle /hello command
@bot.message_handler(commands=['hello'])
def greet_user(message):
    user_profile = get_user_profile(message.chat.id)
    if user_profile['name']:
        bot.send_message(message.chat.id, f"Hello, {user_profile['name']}! How can I assist you today? Please describe your symptoms.")
        print(f"[{datetime.now()}] Greeted user {message.chat.id} by name: {user_profile['name']}")
    else:
        bot.send_message(message.chat.id, "Hello! How can I assist you today? Please describe your symptoms.")
        print(f"[{datetime.now()}] Greeted user {message.chat.id}")

# Thank you handler
@bot.message_handler(func=lambda message: message.text.lower() in ["thanks", "thank you", "thankyou","thankyou 😊"])
def thank_user(message):
    bot.send_message(message.chat.id, "You're welcome! If you have any other questions or need further assistance, feel free to ask.")
    print(f"[{datetime.now()}] User {message.chat.id} thanked the bot")

# General responses for common words
common_responses = {
    "okay": "Alright! How can I help you further?",
    "ok": "Got it! What else can I do for you?",
    "yes": "Great! Please tell me more.",
    "no": "Okay. Let me know if you need anything.",
    "please": "Sure, go ahead!",
    "help": "I'm here to help! What do you need assistance with?"
}

# Command handler to provide health tips on demand
@bot.message_handler(commands=['healthtips'])
def health_tips_on_demand(message):
    tips = [
        "Drink plenty of water to stay hydrated.",
        "Exercise regularly to maintain good health.",
        "Eat a balanced diet with plenty of fruits and vegetables.",
        "Get enough sleep each night.",
        "Practice good hygiene to prevent infections."
    ]

    # Select a random tip from the list
    random_tip = random.choice(tips)
    bot.send_message(message.chat.id, random_tip)
    print(f"[{datetime.now()}] Provided health tip to user {message.chat.id}")

# Common words handler
@bot.message_handler(func=lambda message: message.text.lower() in common_responses.keys())
def common_words_response(message):
    response = common_responses.get(message.text.lower())
    if response:
        bot.send_message(message.chat.id, response)
        print(f"[{datetime.now()}] Common response to user {message.chat.id}: {response}")

# Emergency assistance handler
@bot.message_handler(commands=['emergency'])
def emergency_assistance(message):
    bot.send_message(message.chat.id, "In case of an emergency, please contact the nearest hospital or emergency services. Here are some emergency contact numbers:\n"
                                      "Police: 100\n"
                                      "Fire Department: 101\n"
                                      "Ambulance: 102\n"
                                      "Stay safe!")
    print(f"[{datetime.now()}] Provided emergency assistance to user {message.chat.id}")

# "no that's all" handler
@bot.message_handler(func=lambda message: message.text.lower() == "no that's all")
def handle_thats_all(message):
    bot.send_message(message.chat.id, "Would you like to provide us feedback? If yes, please type /feedback")
    print(f"[{datetime.now()}] User {message.chat.id} indicated they're done and was asked for feedback")

# Command handler for "What can I do to manage it?"
@bot.message_handler(func=lambda message: message.text.lower() == "what can i do to manage it")
def manage_insomnia(message):
    response = ("To help manage insomnia, here are some tips:\n\n"
                "1. Maintain a consistent sleep schedule by going to bed and waking up at the same time every day.\n"
                "2. Create a relaxing bedtime routine to help signal your body that it's time to wind down.\n"
                "3. Avoid caffeine and heavy meals close to bedtime.\n"
                "4. Make your sleep environment comfortable, cool, and free of noise and light disruptions.\n"
                "5. Limit screen time before bed as the blue light from devices can interfere with your sleep.\n\n"
                "If your insomnia persists, consider consulting a healthcare professional for further advice. How else can I assist you?")
    bot.send_message(message.chat.id, response)
    print(f"[{datetime.now()}] User {message.chat.id} asked for insomnia management tips")

# Feedback mechanism
@bot.message_handler(commands=['feedback'])
def get_feedback(message):
    bot.send_message(message.chat.id, "Please provide your feedback.")
    bot.register_next_step_handler(message, save_feedback)
    print(f"[{datetime.now()}] User {message.chat.id} requested to provide feedback")

def save_feedback(message):
    with open('feedback.txt', 'a') as f:
        f.write(f"{message.chat.id}: {message.text}\n")
    bot.send_message(message.chat.id, "Thank you for your feedback!")
    print(f"[{datetime.now()}] Saved feedback from user {message.chat.id}")

# Command handler to delete user profile
@bot.message_handler(commands=['deleteprofile'])
def delete_profile_handler(message):
    user_id = message.chat.id
    bot.send_message(message.chat.id, "Are you sure you want to delete your profile? Type 'yes' to confirm or 'no' to cancel.")
    bot.register_next_step_handler(message, confirm_delete_profile, user_id)
    print(f"[{datetime.now()}] User {message.chat.id} requested to delete profile")

def confirm_delete_profile(message, user_id):
    if message.text.lower() == 'yes':
        if delete_user_profile(user_id):
            bot.send_message(message.chat.id, "Your profile has been deleted successfully.")
            print(f"[{datetime.now()}] User {message.chat.id} profile deleted")
        else:
            bot.send_message(message.chat.id, "Profile not found. Nothing to delete.")
            print(f"[{datetime.now()}] User {message.chat.id} profile not found for deletion")
    else:
        bot.send_message(message.chat.id, "Profile deletion cancelled.")
        print(f"[{datetime.now()}] User {message.chat.id} cancelled profile deletion")

# Message handler for symptoms and general conversation
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    doc = nlp(message.text.lower())
    found_symptoms = []
    response = ""

    for token in doc:
        if token.text in recommendations_and_causes:
            found_symptoms.append(token.text)

    if found_symptoms:
        user_profile = get_user_profile(message.chat.id)
        user_profile['symptoms'].extend(found_symptoms)
        save_profiles()

        for symptom in found_symptoms:
            response += (f" {symptom}:\n"
                         f"Description: {recommendations_and_causes[symptom]['description']}\n\n"
                         f"Cause: {recommendations_and_causes[symptom]['cause']}\n\n"
                         f"Prevention: {recommendations_and_causes[symptom]['prevention']}\n\n"
                         f"Medication: {recommendations_and_causes[symptom]['medication']}\n\n"
                         f"More Information: {recommendations_and_causes[symptom]['link']}\n\n")
        response += "If you have any other symptoms or need further assistance, let me know!"
        print(f"[{datetime.now()}] User {message.chat.id} reported symptoms: {', '.join(found_symptoms)}")
    else:
        # General response if no symptoms are found
        response = "Sorry, I couldn't detect any recognizable symptoms in your message. How else can I assist you?"
        print(f"[{datetime.now()}] User {message.chat.id} message did not contain recognizable symptoms")

    # Check if there's a common response
    for word in common_responses:
        if word in message.text.lower():
            response = common_responses[word]
            print(f"[{datetime.now()}] Common response triggered for user {message.chat.id}: {response}")
            break

    # Default response if nothing else matches
    if not response:
        response = "I'm not sure how to respond to that. Can you please provide more details?"
        print(f"[{datetime.now()}] Default response for user {message.chat.id}")

    bot.send_message(message.chat.id, response)

# Load profiles at startup
load_profiles()

# Delete webhook and start polling
delete_webhook()
print(f"[{datetime.now()}] Bot started polling")
bot.polling()

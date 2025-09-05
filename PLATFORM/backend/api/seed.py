"""
Comando de uso:
docker exec -i bracelet-api-1 alembic downgrade base && docker exec bracelet-api-1 alembic upgrade head && docker exec bracelet-api-1 python ./seed.py
"""

import argparse
import asyncio
import os
import random
import sys
import string

from typing import List
from faker import Faker
import itertools
from datetime import datetime, timezone, timedelta, date


from bracelet_lib.controllers.patient_pathologies import PatientPathologyCtrl
from bracelet_lib.controllers.instruments import InstrumentCtrl
from bracelet_lib.controllers.pathologies import PathologyCtrl
from bracelet_lib.controllers.patient_models import PatientModelCtrl
from bracelet_lib.controllers.patients import PatientCtrl, GenderTypeCtrl
from bracelet_lib.controllers.users import (
    UserRoleCtrl,
    UserStatusCtrl,
    UserAccountCtrl,
    PermissionCtrl,
    PermissionGrantCtrl,
    EntityCtrl
)


from bracelet_lib.controllers.studies import StudyCtrl
from bracelet_lib.controllers.alarm import AlarmCtrl
from bracelet_lib.controllers.chats import ChatCtrl
from bracelet_lib.controllers.message import MessageCtrl

from bracelet_lib.models import database_manager
from bracelet_lib.models.patient_pathologies import PatientPathology
from bracelet_lib.models.instruments import Instrument
from bracelet_lib.models.pathologies import Pathology
from bracelet_lib.models.patient_models import PatientModel
from bracelet_lib.models.patients import Patient, GenderType

from bracelet_lib.models.users import (
    UserRole,
    UserStatus,
    UserAccount,
    Permission,
    PermissionGrant,
    Entity
)

from bracelet_lib.models.chats import Chat
from bracelet_lib.models.messages import Message
from bracelet_lib.models.studies import Study
from bracelet_lib.models.alarm import Alarm

from types import SimpleNamespace


faker = Faker()


# Configuration constants
num_new_patient_users = 15  # Reducido de 25 a 15 para mejor rendimiento
STUDY_DATES_RANGE_DAYS = 15  # Reducido de 22 a 15 días
MIN_DISTINCT_STUDY_DATES = 3
MAX_DISTINCT_STUDY_DATES = 5  # Reducido de 8 a 5 para menos datos pero más consistentes
MIN_READING_INTERVAL_SEC = 300   # 5 minutos (aumentado de 1-3 min)
MAX_READING_INTERVAL_SEC = 900   # 15 minutos (aumentado para menos lecturas)
MIN_READINGS_PER_DAY = 200  # Reducido de 1000 para datos más manejables
MAX_READINGS_PER_DAY = 1000  # Reducido de 3000 para datos más manejables

MIN_ID = 1
MAX_ID = 30

# Set para rastrear nombres ya usados
used_patient_names = set()

def generate_unique_patient_name():
    """
    Genera una combinación única de nombre y apellido para pacientes
    """
    max_attempts = 50
    for _ in range(max_attempts):
        first_name = faker.first_name()
        last_name = faker.last_name()
        full_name = f"{first_name} {last_name}"
        
        if full_name not in used_patient_names:
            used_patient_names.add(full_name)
            return first_name, last_name
    
    # Si después de 50 intentos no encuentra un nombre único, agregar timestamp
    timestamp = int(datetime.now().timestamp() * 1000) % 10000  # Últimos 4 dígitos
    first_name = faker.first_name()
    last_name = f"{faker.last_name()}{timestamp}"
    full_name = f"{first_name} {last_name}"
    used_patient_names.add(full_name)
    return first_name, last_name

#docker exec -i bracelet-api-1 alembic downgrade base && docker exec bracelet-api-1 alembic upgrade head && docker exec bracelet-api-1 python ./seed.py 
INSTRUMENTS = [
    {
        "name": {
            "en": "Pulsera Ejemplo",
            "es": "Pulsera Ejemplo"
        },
        "model": "Diego de Pablo, prototipo 1'",
        "filename": "Ejemplo.glb",
        "url": "https://bracelet-tests-diegodepab.s3.us-east-1.amazonaws.com/carcasa1.glb"
    },

]

PATHOLOGIES = [
    {
        "en": "Hypertension",
        "es": "Hipertensión",
    },
    {
        "en": "Diabetes",
        "es": "Diabetes",
    },
    {
        "en": "Obesity",
        "es": "Obesidad",
    },
    {
        "en": "Arthritis",
        "es": "Artritis",
    },
    {
        "en": "Osteoporosis",
        "es": "Osteoporosis",
    },
    {
        "en": "Back Pain",
        "es": "Dolor de espalda",
    },
    {
        "en": "Joint Pain",
        "es": "Dolor articular",
    },
    {
        "en": "Varicose Veins",
        "es": "Venas varicosas",
    },
    {
        "en": "Anemia",
        "es": "Anemia",
    },
    {
        "en": "Bronchitis",
        "es": "Bronquitis",
    },
    {
        "en": "Asthma",
        "es": "Asma",
    },
    {
        "en": "Insomnia",
        "es": "Insomnio",
    },
    {
        "en": "Depression",
        "es": "Depresión",
    },
    {
        "en": "Anxiety",
        "es": "Ansiedad",
    },
    {
        "en": "Vertigo",
        "es": "Vértigo",
    },
    {
        "en": "Cataracts",
        "es": "Cataratas",
    },
    {
        "en": "Glaucoma",
        "es": "Glaucoma",
    },
    {
        "en": "Elderly person",
        "es": "Persona de avanzada edad",
    },
    {
        "en": "Elderly person",
        "es": "Persona de avanzada edad",
    },
       {
        "en": "Peripheral Artery Disease",
        "es": "Enfermedad arterial periférica",
    },
    {
        "en": "Deep Vein Thrombosis",
        "es": "Trombosis venosa profunda",
    },
    {
        "en": "Peripheral Neuropathy",
        "es": "Neuropatía periférica",
    },
    {
        "en": "Intermittent Claudication",
        "es": "Claudicación intermitente",
    },
    {
        "en": "Sciatica",
        "es": "Ciática",
    },
    {
        "en": "Knee Osteoarthritis",
        "es": "Osteoartritis de rodilla",
    },
 ]


USER_STATUSES = ["active", "pending", "inactive"]
USER_ROLES    = ["admin", "user","patient"]
GENDER_TYPES  = ["male", "female"]

PERMISSIONS_GRANT = ["all", "own", "none"]
PERMISSIONS       = {
    # role          entity                 read   write  delete ui_visibility
    ("admin",   "user_account")         : ("all", "all", "all", True),
    ("user",    "user_account")         : ("all", "own", "own", True),
    ("patient", "user_account")         : ("own", "own", "own", False),

    ("admin",   "patient")              : ("all", "all", "all", True),
    ("user",    "patient")              : ("own", "own", "own", True),

    ("admin",   "patient_model")        : ("all", "all", "all", True),
    ("user",    "patient_model")        : ("own", "own", "own", True),
    ("patient", "patient_model")        : ("own", "own", "own", True),

    ("admin",   "patient_pathology")    : ("all", "all", "all", True),
    ("user",    "patient_pathology")    : ("own", "own", "own", True),

    ("admin",   "study")                : ("all", "all", "all", True),
    ("user",    "study")                : ("own", "own", "own", True),
    ("patient", "study")                : ("own", "none","none",True),

    ("admin",   "chat")                 : ("all", "all", "all", True),
    ("user",    "chat")                 : ("all", "all", "all", True),
    ("patient", "chat")                 : ("all", "all", "all", True),

    ("admin",   "messages")              : ("all", "all", "all", True),
    ("user",    "messages")              : ("all", "all", "all", True),
    ("patient", "messages")              : ("all", "all", "all", True),

    ("admin",   "alarms")                : ("all", "all", "all", True),
    ("user",    "alarms")                : ("own", "own", "own", True),
    ("patient", "alarms")                : ("own", "own", "own", True)
}

PATIENT_MODELS = [
    {
        "name": "Prototipo 1 modelo LILYGO® T-Display-S3 AMOLED",
        "filename": "modelo_AWS",
        "url": "https://bracelet-tests-diegodepab.s3.us-east-1.amazonaws.com/user/1/patient-models/1/ttgo-t-display.glb"
    }
]

for entity_read_only in (
        "user_role",
        "user_status",
        "entity",
        "permission_grant",
        "permission",
        "instrument",
        "pathology"
):
    for role in USER_ROLES:
        perm_tuple = ("all", "none", "none", True)
        if role == "admin":
            perm_tuple = ("all", "all", "all", True)

        PERMISSIONS[(role, entity_read_only)] = perm_tuple


async def seed_user_statuses():
    print(" -- seeding user_status")

    for name in USER_STATUSES:
        await UserStatusCtrl.create(
            UserStatus.CreateValidator(
                name = name
            ),
            validate         = False,
            with_transaction = False
        )


async def seed_gender_types():
    print(" -- seeding gender type")

    for name in GENDER_TYPES:
        await GenderTypeCtrl.create(
            GenderType.CreateValidator(
                name = name
            ),
            validate         = False,
            with_transaction = False
        )


async def seed_user_roles():
    print(" -- seeding user_role")

    for name in USER_ROLES:
        await UserRoleCtrl.create(
            UserRole.CreateValidator(
                name = name
            ),
            validate         = False,
            with_transaction = False
        )


async def seed_permissions():
    print(" -- seeding permission")

    # Create permissions grant
    for name in PERMISSIONS_GRANT:
        await PermissionGrantCtrl.create(
            PermissionGrant.CreateValidator(
                name = name
            ),
            validate         = False,
            with_transaction = False
        )

    # Create entities
    for entity_name in set([ k[1] for k in PERMISSIONS.keys() ]):
        await EntityCtrl.create(
            Entity.CreateValidator(
                name = entity_name
            ),
            validate         = False,
            with_transaction = False
        )

    # Create permissions
    for key, values in PERMISSIONS.items():
        role_, entity        = key
        read, write, delete, ui_visibility = values
        await PermissionCtrl.create(
            Permission.CreateValidator(
                user_role_name = role_,
                entity_name    = entity,
                read           = read,
                write          = write,
                delete         = delete,
                ui_visibility  = ui_visibility
            ),
            validate         = False,
            with_transaction = False
        )

async def seed_studies():
    print(" -- skipping health data seeding")
    return []

async def seed_patient_user_accounts(pathologies: list[Pathology], num_patients: int = 10) -> list[Patient]:
    """
    Crea num_patients cuentas de UserAccount con rol "patient" y, para cada cuenta,
    crea el registro en Patient apuntando tanto al doctor como al usuario del paciente.
    Devuelve la lista de objetos Patient creados.
    """
    created_patients = []

    for _ in range(num_patients):
        # 1) Creamos la cuenta de usuario con rol "patient"
        user_status = random.choice([USER_STATUSES[0], USER_STATUSES[1]])  # "active" ó "pending"
        approval_ts = None if user_status == USER_STATUSES[1] else datetime.now(timezone.utc)

        # Generar nombres más variados - algunos simples, algunos compuestos
        if random.random() < 0.3:  # 30% de probabilidad de nombres compuestos
            # Nombres compuestos como "María Elena", "José Luis", etc.
            first_names = [faker.first_name(), faker.first_name()]
            last_names = [faker.last_name()]
            if random.random() < 0.5:  # 50% de los compuestos tienen también apellido compuesto
                last_names.append(faker.last_name())
            
            full_first_name = " ".join(first_names)
            full_last_name = " ".join(last_names)
            patient_code = f"{full_first_name} {full_last_name}"
            
            # CRÍTICO: Para matching de chats, el UserAccount debe parsearse igual que el frontend
            # Frontend parsea patient.code como: firstName = primera palabra, lastName = resto
            # Entonces UserAccount debe tener: first_name = primera palabra, last_name = resto
            account_first_name = first_names[0]  # Solo "María"
            account_last_name = f"{' '.join(first_names[1:])} {full_last_name}".strip()  # "Elena García López"
        else:
            # Nombres simples
            first_name = faker.first_name()
            last_name = faker.last_name()
            patient_code = f"{first_name} {last_name}"
            
            account_first_name = first_name
            account_last_name = last_name

        user_account = await UserAccountCtrl.create(
            UserAccount.CreateValidator(
                email            = f"{account_first_name.lower().replace(' ', '.')}.{account_last_name.lower().replace(' ', '.')}@email.com",
                password         = "TFGde10",
                user_role_name   = "patient",          # <-- rol paciente
                user_status_name = user_status,
                first_name       = account_first_name,  # Primera palabra de patient.code
                last_name        = account_last_name,   # Resto de patient.code
                phone            = faker.phone_number(),
                approval_toc_ts  = approval_ts
            ),
            validate         = False,
            with_transaction = False
        )
        
        # Seleccionar un doctor aleatorio como owner (de los doctores demo existentes)
        # Podemos asumir que hay al menos un doctor con ID entre 1-10
        owner_doctor_id = random.randint(2, 6)  # IDs típicos de doctores demo

        # 2) Creamos el registro en Patient vinculado tanto al doctor como al usuario del paciente
        patient = await PatientCtrl.create(
            Patient.CreateValidator(
                code            = patient_code,  # Usar exactamente el mismo nombre que el usuario
                gender          = random.choice(GENDER_TYPES),
                weight          = random.randint(50, 100),
                birth_date      = generate_random_birth_date(),
                owner_user_id   = owner_doctor_id,      # <-- Doctor responsable
                patient_user_id = user_account.id       # <-- NUEVO: Cuenta del paciente
            ),
            validate         = False,
            with_transaction = False
        )
        created_patients.append(patient)

        # 3) Asignar patologías más realistas (relacionadas con la edad)
        birth_year = patient.birth_date.year
        current_year = datetime.now().year
        age = current_year - birth_year
        
        assigned_pathologies = []
        
        # Patologías más comunes según edad
        if age > 65:
            # Personas mayores: más probabilidad de hipertensión, diabetes, artritis
            likely_pathologies = ["Hipertensión", "Diabetes", "Artritis", "Osteoporosis", "Persona de avanzada edad"]
            num_pathologies = random.randint(2, 4)
        elif age > 45:
            # Edad media: probabilidad moderada de algunas condiciones
            likely_pathologies = ["Hipertensión", "Diabetes", "Dolor de espalda", "Ansiedad"]
            num_pathologies = random.randint(1, 3)
        else:
            # Jóvenes: menos probabilidad de patologías crónicas
            likely_pathologies = ["Asma", "Ansiedad", "Dolor de espalda", "Anemia"]
            num_pathologies = random.randint(0, 2)
        
        for _ in range(num_pathologies):
            # Primero intentamos asignar patologías más probables para la edad
            if random.random() < 0.7 and likely_pathologies:  # 70% probabilidad de patología relacionada con edad
                pathology_name = random.choice(likely_pathologies)
                matching_pathologies = [p for p in pathologies if p.name == pathology_name and p.id not in assigned_pathologies]
                if matching_pathologies:
                    pat = matching_pathologies[0]
                else:
                    pat = get_random_pathology(assigned_pathologies, pathologies)
            else:
                pat = get_random_pathology(assigned_pathologies, pathologies)
                
            if pat is None:
                continue
                
            assigned_pathologies.append(pat.id)
            random_days = random.randint(-365, 0)
            detection_date = datetime.now().date() + timedelta(days=random_days)
            await PatientPathologyCtrl.create(
                PatientPathology.CreateValidator(
                    patient_id     = patient.id,
                    pathology_id   = pat.id,
                    detection_date = detection_date,
                ),
                validate         = False,
                with_transaction = False
            )

        # 4) Insertar modelos también (igual que seed_patient_models)
        await seed_patient_models(patient.id)

    return created_patients
async def create_example_patients(pathologies: List[Pathology], doctors: List[UserAccount]) -> List[Patient]:
    """
    Crea algunos pacientes de ejemplo con casos específicos comunes
    Asigna cada paciente a un doctor aleatorio de la lista
    """
    example_patients = []
    
    # Paciente 1: Persona mayor con hipertensión y diabetes
    assigned_doctor = random.choice(doctors) if doctors else None
    if assigned_doctor:
        patient1 = await create_single_patient_account_with_doctor(
            email       = "maria.garcia@email.com",
            password    = "TFGde10",
            first_name  = "María",
            last_name   = "García",
            phone       = "+34 666 111 222",
            gender      = "female",
            weight      = 68,
            birth_date  = date(1955, 3, 15),  # 70 años
            assigned_doctor_id = assigned_doctor.id,
            user_status = "active"
        )
    else:
        patient1 = await create_single_patient_account(
            email       = "maria.garcia@email.com",
            password    = "TFGde10",
            first_name  = "María",
            last_name   = "García",
            phone       = "+34 666 111 222",
            gender      = "female",
            weight      = 68,
            birth_date  = date(1955, 3, 15),  # 70 años
            user_status = "active"
        )
    
    example_patients.append(patient1)
    
    # Asignar patologías relacionadas con la edad
    hypertension = next((p for p in pathologies if "Hipertensión" in p.name), None)
    diabetes = next((p for p in pathologies if "Diabetes" in p.name), None)
    elderly = next((p for p in pathologies if "avanzada edad" in p.name), None)
    
    for pathology in [hypertension, diabetes, elderly]:
        if pathology:
            await PatientPathologyCtrl.create(
                PatientPathology.CreateValidator(
                    patient_id     = patient1.id,
                    pathology_id   = pathology.id,
                    detection_date = datetime.now().date() - timedelta(days=random.randint(30, 365)),
                ),
                validate         = False,
                with_transaction = False
            )
    
    # Paciente 2: Adulto joven con asma
    assigned_doctor = random.choice(doctors) if doctors else None
    if assigned_doctor:
        patient2 = await create_single_patient_account_with_doctor(
            email       = "carlos.lopez@email.com",
            password    = "TFGde10",
            first_name  = "Carlos",
            last_name   = "López",
            phone       = "+34 666 333 444",
            gender      = "male",
            weight      = 75,
            birth_date  = date(1995, 8, 22),  # 29 años
            assigned_doctor_id = assigned_doctor.id,
            user_status = "active"
        )
    else:
        patient2 = await create_single_patient_account(
            email       = "carlos.lopez@email.com",
            password    = "TFGde10",
            first_name  = "Carlos",
            last_name   = "López",
            phone       = "+34 666 333 444",
            gender      = "male",
            weight      = 75,
            birth_date  = date(1995, 8, 22),  # 29 años
            user_status = "active"
        )
    
    example_patients.append(patient2)
    
    asthma = next((p for p in pathologies if "Asma" in p.name), None)
    if asthma:
        await PatientPathologyCtrl.create(
            PatientPathology.CreateValidator(
                patient_id     = patient2.id,
                pathology_id   = asthma.id,
                detection_date = datetime.now().date() - timedelta(days=random.randint(90, 1095)),
            ),
            validate         = False,
            with_transaction = False
        )
    
    # Paciente 3: Persona de mediana edad con problemas de espalda
    assigned_doctor = random.choice(doctors) if doctors else None
    if assigned_doctor:
        patient3 = await create_single_patient_account_with_doctor(
            email       = "ana.martinez@email.com",
            password    = "TFGde10",
            first_name  = "Ana",
            last_name   = "Martínez",
            phone       = "+34 666 555 666",
            gender      = "female",
            weight      = 62,
            birth_date  = date(1978, 12, 10),  # 46 años
            assigned_doctor_id = assigned_doctor.id,
            user_status = "active"
        )
    else:
        patient3 = await create_single_patient_account(
            email       = "ana.martinez@email.com",
            password    = "TFGde10",
            first_name  = "Ana",
            last_name   = "Martínez",
            phone       = "+34 666 555 666",
            gender      = "female",
            weight      = 62,
            birth_date  = date(1978, 12, 10),  # 46 años
            user_status = "active"
        )
    
    example_patients.append(patient3)
    
    back_pain = next((p for p in pathologies if "espalda" in p.name), None)
    anxiety = next((p for p in pathologies if "Ansiedad" in p.name), None)
    
    for pathology in [back_pain, anxiety]:
        if pathology:
            await PatientPathologyCtrl.create(
                PatientPathology.CreateValidator(
                    patient_id     = patient3.id,
                    pathology_id   = pathology.id,
                    detection_date = datetime.now().date() - timedelta(days=random.randint(60, 730)),
                ),
                validate         = False,
                with_transaction = False
            )
    
    # Añadir modelos a todos los pacientes de ejemplo
    for patient in example_patients:
        await seed_patient_models(patient.id)
    
    return example_patients


async def seed_instruments() -> List[Instrument]:
    print(" -- seeding instruments")

    instruments = []
    for instrument in INSTRUMENTS:
        instruments.append(
            await InstrumentCtrl.create(
                Instrument.CreateValidator(
                    name     = instrument["name"]["es"],
                    filename = instrument["filename"],
                    url      = instrument["url"],
                    model    = instrument["model"],
                ),
                validate         = False,
                with_transaction = False
            )
        )

    return instruments


async def seed_pathologies() -> List[Pathology]:
    print(" -- seeding pathologies")

    pathologies = []

    for pathology in PATHOLOGIES:
        pathologies.append(
            await PathologyCtrl.create(
                Pathology.CreateValidator(name = pathology["es"]),
                validate         = False,
                with_transaction = False
            )
        )

    return pathologies


async def seed_admin_user() -> UserAccount:
    print(" -- seeding admin_user")

    # insert admin user
    admin = await UserAccountCtrl.create(
        UserAccount.CreateValidator(
            email            = "admin@bracelet.com",
            password         = "TFGde10",
            user_role_name   = USER_ROLES[0],
            user_status_name = USER_STATUSES[0],
            first_name       = "bracelet",
            last_name        = "Admin",
            phone            = "+34 555 555 555",
            approval_toc_ts  = datetime.now(timezone.utc)
        ),
        validate         = False,
        with_transaction = False
    )


    admin = await UserAccountCtrl.create(
        UserAccount.CreateValidator(
            email            = "servicio@bracelet.com",
            password         = "TFGde10",
            user_role_name   = USER_ROLES[0],
            user_status_name = USER_STATUSES[0],
            first_name       = "Equipo de servicio",
            last_name        = "de la plataforma",
            phone            = "+34 555 555 553",
            approval_toc_ts  = datetime.now(timezone.utc)
        ),
        validate         = False,
        with_transaction = False
    )

    return admin
async def seed_demo_users():
    print("\n -- seeding users / doctors")

    now_ts = datetime.now(timezone.utc)
    doctors = []

    for doctor_email in [
        "doctor",
        "doctor2",
        "doctor3",
        "doctor4",
    ]:
        email = f"{doctor_email}@bracelet.com"
        try:
            doctor = await UserAccountCtrl.create(
                UserAccount.CreateValidator(
                    email            = email,
                    password         = "TFGde10",
                    user_role_name   = USER_ROLES[1], # user
                    user_status_name = USER_STATUSES[0], # active
                    first_name       = faker.first_name(),
                    last_name        = faker.last_name(),
                    phone            = "+34 555 555 555",
                    approval_toc_ts  = now_ts
                ),
                validate         = False,
                with_transaction = False
            )
            print(f"Doctor creado: {email} id={doctor.id}")
            doctors.append(doctor)
        except Exception as e:
            print(f"Error creando doctor {email}: {e}")

    return doctors


async def seed_patients(owner_id: int, pathologies: List[Pathology]):
    print(f" -- seeding patients for doctor {owner_id}")

    patients = []
    # insert from 1 to 10 patients per doctor
    for _ in range(random.randint(8, 10)):  # Aumentado de 2-5 a 8-10 para más pacientes
        first_name, last_name = generate_unique_patient_name()
        
        # 1) Crear cuenta de usuario para el paciente con email único
        patient_email = f"{first_name.lower()}.{last_name.lower()}@paciente.com"
        user_status = random.choice([USER_STATUSES[0], USER_STATUSES[1]])  # "active" o "pending"
        approval_ts = None if user_status == USER_STATUSES[1] else datetime.now(timezone.utc)

        patient_user_account = await UserAccountCtrl.create(
            UserAccount.CreateValidator(
                email            = patient_email,
                password         = "TFGde10",
                user_role_name   = "patient",
                user_status_name = user_status,
                first_name       = first_name,
                last_name        = last_name,
                phone            = faker.phone_number(),
                approval_toc_ts  = approval_ts
            ),
            validate         = False,
            with_transaction = False
        )

        # 2) Crear el registro del paciente vinculado al doctor Y al usuario del paciente
        code = f"{first_name} {last_name}"
        patient = await PatientCtrl.create(
            Patient.CreateValidator(
                code            = code,
                gender          = random.choice(GENDER_TYPES),
                weight          = random.randint(50, 100),
                birth_date      = generate_random_birth_date(),
                owner_user_id   = owner_id,                 # El doctor es el dueño del registro del paciente
                patient_user_id = patient_user_account.id   # NUEVO: Cuenta del usuario paciente
            ),
            validate         = False,
            with_transaction = False
        )

        patients.append(patient)

        # Agregar información del doctor asignado y cuenta de paciente para usar en chats
        patient.assigned_doctor_id = owner_id  # Guardar referencia al doctor asignado
        patient.patient_user_account = patient_user_account  # Guardar cuenta del paciente para chats

        # 3) Asignar patologías más realistas (relacionadas con la edad)
        birth_year = patient.birth_date.year
        current_year = datetime.now().year
        age = current_year - birth_year
        
        assigned_pathologies = []
        
        # Patologías más comunes según edad
        if age > 65:
            # Personas mayores: más probabilidad de hipertensión, diabetes, artritis
            likely_pathologies = ["Hipertensión", "Diabetes", "Artritis", "Osteoporosis", "Persona de avanzada edad"]
            num_pathologies = random.randint(2, 4)
        elif age > 45:
            # Edad media: probabilidad moderada de algunas condiciones
            likely_pathologies = ["Hipertensión", "Diabetes", "Dolor de espalda", "Ansiedad"]
            num_pathologies = random.randint(1, 3)
        else:
            # Jóvenes: menos probabilidad de patologías crónicas
            likely_pathologies = ["Asma", "Ansiedad", "Dolor de espalda", "Anemia"]
            num_pathologies = random.randint(0, 2)
        
        for _ in range(num_pathologies):
            # Primero intentamos asignar patologías más probables para la edad
            if random.random() < 0.7 and likely_pathologies:  # 70% probabilidad de patología relacionada con edad
                pathology_name = random.choice(likely_pathologies)
                matching_pathologies = [p for p in pathologies if p.name == pathology_name and p.id not in assigned_pathologies]
                if matching_pathologies:
                    pat = matching_pathologies[0]
                else:
                    pat = get_random_pathology(assigned_pathologies, pathologies)
            else:
                pat = get_random_pathology(assigned_pathologies, pathologies)
                
            if pat is None:
                continue
                
            assigned_pathologies.append(pat.id)
            random_days = random.randint(-365, 0)
            detection_date = datetime.now().date() + timedelta(days=random_days)
            await PatientPathologyCtrl.create(
                PatientPathology.CreateValidator(
                    patient_id     = patient.id,
                    pathology_id   = pat.id,
                    detection_date = detection_date,
                ),
                validate         = False,
                with_transaction = False
            )

        # 4) Insertar modelos también (igual que seed_patient_models)
        await seed_patient_models(patient.id)

    return patients


async def create_single_patient_with_doctor(owner_id: int, pathologies: List[Pathology]) -> Patient:
    """
    Crea un único paciente asignado a un doctor específico
    """
    first_name, last_name = generate_unique_patient_name()
    
    # 1) Crear cuenta de usuario para el paciente con email único
    patient_email = f"{first_name.lower()}.{last_name.lower()}@paciente.com"
    user_status = random.choice([USER_STATUSES[0], USER_STATUSES[1]])  # "active" o "pending"
    approval_ts = None if user_status == USER_STATUSES[1] else datetime.now(timezone.utc)

    patient_user_account = await UserAccountCtrl.create(
        UserAccount.CreateValidator(
            email            = patient_email,
            password         = "TFGde10",
            user_role_name   = "patient",
            user_status_name = user_status,
            first_name       = first_name,
            last_name        = last_name,
            phone            = faker.phone_number(),
            approval_toc_ts  = approval_ts
        ),
        validate         = False,
        with_transaction = False
    )

    # 2) Crear el registro del paciente vinculado al doctor Y al usuario del paciente
    code = f"{first_name} {last_name}"
    patient = await PatientCtrl.create(
        Patient.CreateValidator(
            code            = code,
            gender          = random.choice(GENDER_TYPES),
            weight          = random.randint(50, 100),
            birth_date      = generate_random_birth_date(),
            owner_user_id   = owner_id,                 # El doctor es el dueño del registro del paciente
            patient_user_id = patient_user_account.id   # NUEVO: Cuenta del usuario paciente
        ),
        validate         = False,
        with_transaction = False
    )

    # Agregar información del doctor asignado y cuenta de paciente para usar en chats
    patient.assigned_doctor_id = owner_id  # Guardar referencia al doctor asignado
    patient.patient_user_account = patient_user_account  # Guardar cuenta del paciente para chats

    # 3) Asignar patologías según edad (igual que la función original)
    birth_year = patient.birth_date.year
    current_year = datetime.now().year
    age = current_year - birth_year
    
    assigned_pathologies = []
    
    # Patologías más comunes según edad
    if age > 65:
        likely_pathologies = ["Hipertensión", "Diabetes", "Artritis", "Osteoporosis", "Persona de avanzada edad"]
        num_pathologies = random.randint(2, 4)
    elif age > 45:
        likely_pathologies = ["Hipertensión", "Diabetes", "Dolor de espalda", "Ansiedad"]
        num_pathologies = random.randint(1, 3)
    elif age > 25:
        likely_pathologies = ["Ansiedad", "Dolor de espalda", "Asma"]
        num_pathologies = random.randint(0, 2)
    else:
        likely_pathologies = ["Asma", "Ansiedad"]
        num_pathologies = random.randint(0, 1)
    
    def get_random_pathology(assigned_ids, all_pathologies):
        available_pathologies = [p for p in all_pathologies if p.id not in assigned_ids]
        return random.choice(available_pathologies) if available_pathologies else None
    
    for _ in range(num_pathologies):
        if age > 45:
            # Buscar patologías específicas para esa edad
            matching_pathologies = [
                p for p in pathologies 
                for likely_name in likely_pathologies 
                if likely_name.lower() in p.name.lower() and p.id not in assigned_pathologies
            ]
            if matching_pathologies:
                pat = matching_pathologies[0]
            else:
                pat = get_random_pathology(assigned_pathologies, pathologies)
        else:
            pat = get_random_pathology(assigned_pathologies, pathologies)
            
        if pat is None:
            continue
            
        assigned_pathologies.append(pat.id)
        random_days = random.randint(-365, 0)
        detection_date = datetime.now().date() + timedelta(days=random_days)

        await PatientPathologyCtrl.create(
            PatientPathology.CreateValidator(
                patient_id     = patient.id,
                pathology_id   = pat.id,
                detection_date = detection_date,
            ),
            validate         = False,
            with_transaction = False
        )

    await seed_patient_models(patient.id)
    return patient


async def dev_patients(owner_id: int, pathologies: List[Pathology], patients: List[Patient]):
    print(" -- seeding dev_patients")

    now = datetime.now()
    # insert patients
    for _ in range(random.randint(1, 5)):

        patient = await PatientCtrl.create(
            Patient.CreateValidator(
                code          = code_generator.generate_code(),
                gender        = random.choice(GENDER_TYPES),
                weight        = random.randint(70, 100),
                birth_date    = now - timedelta(weeks=1500),
                owner_user_id = owner_id,
                patient_user_id = None
            ),
            validate         = False,
            with_transaction = False
        )


        # insert the relation between patient and pathologies
        for _ in range(random.randint(0, 3)):
            await PatientPathologyCtrl.create(
                PatientPathology.CreateValidator(
                    patient_id     = patient.id,
                    pathology_id   = (random.choice(pathologies)).id,
                    detection_date = datetime.now().date()
                ),
                validate         = False,
                with_transaction = False
            )

        patients.append(patient)


async def create_single_patient_account_with_doctor(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    phone: str,
    gender: str,
    weight: int,
    birth_date: date,
    assigned_doctor_id: int,
    user_status: str = "active"
) -> Patient:
    """
    Crea un paciente con un doctor asignado específico.
    1) Crea un UserAccount con rol 'patient'.
    2) Crea un Patient con owner_user_id = assigned_doctor_id y patient_user_id = UserAccount.id.
    3) Guarda la referencia a la cuenta original del paciente para chats.
    """
    
    # --- 1) Crear el UserAccount para el paciente ---
    approval_ts = None
    if user_status == "active":
        approval_ts = datetime.now(timezone.utc)

    user_account = await UserAccountCtrl.create(
        UserAccount.CreateValidator(
            email            = email,
            password         = password,
            user_role_name   = "patient",
            user_status_name = user_status,
            first_name       = first_name,
            last_name        = last_name,
            phone            = phone,
            approval_toc_ts  = approval_ts
        ),
        validate         = True,
        with_transaction = False
    )

    # --- 2) Crear el registro en Patient, con doctor asignado Y usuario del paciente ---
    full_name_code = f"{first_name} {last_name}"

    patient = await PatientCtrl.create(
        Patient.CreateValidator(
            code            = full_name_code,
            gender          = gender,
            weight          = weight,
            birth_date      = birth_date,
            owner_user_id   = assigned_doctor_id,  # Directamente asignado al doctor
            patient_user_id = user_account.id      # NUEVO: Cuenta del usuario paciente
        ),
        validate         = True,
        with_transaction = False
    )
    
    # --- 3) Guardar info adicional para chats ---
    patient.assigned_doctor_id = assigned_doctor_id
    patient.patient_user_account = user_account  # Cuenta original del paciente
    
    return patient


async def create_single_patient_account(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    phone: str,
    gender: str,
    weight: int,
    birth_date: date,
    user_status: str = "active"  # puede ser "active" o "pending"
) -> Patient:
    """
    1) Crea un UserAccount con rol 'patient'.
    2) Crea un Patient con code = "<first_name> <last_name>", owner_user_id apuntando al UserAccount.id,
       y patient_user_id también apuntando al UserAccount.id (paciente es su propio owner).
    Devuelve el objeto Patient recién creado.
    """

    # --- 1) Crear el UserAccount para el paciente ---
    approval_ts = None
    if user_status == "active":
        approval_ts = datetime.now(timezone.utc)

    user_account = await UserAccountCtrl.create(
        UserAccount.CreateValidator(
            email            = email,
            password         = password,
            user_role_name   = "patient",        # <- enfático: rol = patient
            user_status_name = user_status,      # "active" o "pending"
            first_name       = first_name,
            last_name        = last_name,
            phone            = phone,
            approval_toc_ts  = approval_ts      # Fecha de aprobación si está activo
        ),
        validate         = True,
        with_transaction = False
    )

    # --- 2) Crear el registro en Patient, usando "code" = "<first_name> <last_name>" ---
    full_name_code = f"{first_name} {last_name}"

    patient = await PatientCtrl.create(
        Patient.CreateValidator(
            code            = full_name_code,
            gender          = gender,            # "male" o "female"
            weight          = weight,            # en kilos, por ejemplo 75
            birth_date      = birth_date,        # datetime.date (e.g. date(1985, 7, 23))
            owner_user_id   = user_account.id,   # referenciando el usuario creado (paciente es su propio owner)
            patient_user_id = user_account.id    # NUEVO: También apunta al mismo usuario
        ),
        validate         = True,
        with_transaction = False
    )

    return patient


async def seed_users() -> List[UserAccount]:
    print(" -- seeding users")

    users = []
    for _ in range(random.randint(20, 35)):
        user_status = random.choice([ USER_STATUSES[0], USER_STATUSES[1] ])
        approval_toc_ts = None if user_status == USER_STATUSES[1] else datetime.now(timezone.utc)
        users.append(
            await UserAccountCtrl.create(
                UserAccount.CreateValidator(
                    email            = f"{faker.word()}.{faker.email()}",
                    password         = "TFGde10",
                    user_role_name   = USER_ROLES[1],   # user
                    user_status_name = user_status,
                    first_name       = faker.first_name(),
                    last_name        = faker.last_name(),
                    phone            = faker.phone_number(),
                    approval_toc_ts  = approval_toc_ts
                ),
                validate         = False,
                with_transaction = False
            )
        )

    return users


async def seed_patient_models(patient_id: int) -> None:
    """
    Inserta un modelo asociados a un paciente concreto.
    - patient_id: id del paciente al que asocias los modelos.
    """
    for model in PATIENT_MODELS:
        await PatientModelCtrl.create(
            PatientModel.CreateValidator(
                name       = model["name"],
                patient_id = patient_id,
                filename   = model["filename"],
                url        = model["url"]
            ),
            validate         = False,
            with_transaction = False
        )

# request a non-repeated pathology from a list of already selected ones
def get_random_pathology(current_pathologies: List[int], pathologies: List[Pathology]) -> Pathology | None:
    tries     = 0

    while tries < 10:
        tries += 1
        pathology = random.choice(pathologies)
        if pathology.id not in current_pathologies:
            return pathology

    return None


class PatientCodeGenerator:
    def __init__(self):
        self.used_codes = set()

    def generate_code(self):
        code = None

        while True:
            # allowed characters only uppercase letters and digits
            characters = string.ascii_uppercase + string.digits

            # set a random length between 10 and 15 characters
            length = random.randint(10, 15)
            code = "".join(random.choice(characters) for _ in range(length))

            if code not in self.used_codes:
                break

        return code

code_generator = PatientCodeGenerator()

def generate_random_birth_date():
    today = datetime.now()

    # all generated ages are between 20 and 80 years old
    earliest_date = today - timedelta(days = 365.25 * 80)
    latest_date   = today - timedelta(days = 365.25 * 20)

    # generate a random number of days between the earliest and latest date
    days_range = (latest_date - earliest_date).days
    random_days = random.randint(0, days_range)
    random_date = earliest_date + timedelta(days=random_days)

    # format the date as a string in the format "DD/MM/YYYY"
    return random_date.date()

# ── Función para generar studies aleatorios ────────────────────────────────────
async def seed_studies_for_patients(patients: List[Patient]) -> List[Study]:
    print(" -- seeding studies for patients with enhanced data for recent days")
    all_studies = []
    base_utc = datetime.now(timezone.utc)

    for i, patient in enumerate(patients):
        if i % 10 == 0:  # Mensaje de progreso cada 10 pacientes
            print(f"   Processing patient {i+1}/{len(patients)}")
            
        # Asegurar que todos los pacientes tengan datos del día más reciente (hoy)
        days = random.sample(
            range(1, STUDY_DATES_RANGE_DAYS),  # Días del 1 al 14 (excluyendo el 0)
            random.randint(MIN_DISTINCT_STUDY_DATES - 1, MAX_DISTINCT_STUDY_DATES - 1)
        )
        days.insert(0, 0)  # Agregar siempre el día más reciente (hoy)

        for day_offset in days:
            date_midnight = (base_utc - timedelta(days=day_offset)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            start_hour = random.randint(6, 12)
            date_start = date_midnight.replace(hour=start_hour)

            end_hour = random.randint(22, 23)
            date_end = date_midnight.replace(hour=end_hour, minute=0, second=0, microsecond=0)

            # Para el día más reciente (day_offset=0), generamos más datos
            is_most_recent_day = (day_offset == 0)
            
            studies = await _generate_daily_studies(
                patient_id=patient.id,
                start_ts=date_start.replace(tzinfo=None),
                end_ts=date_end.replace(tzinfo=None),
                is_most_recent_day=is_most_recent_day
            )
            all_studies.extend(studies)

    print(f" -- Generated {len(all_studies)} total studies")
    return all_studies


# ── Función para determinar perfil de salud del paciente ──────────────────
def get_patient_health_profile(patient_id: int, age: int, pathology_names: list) -> dict:
    """
    Determina el perfil de salud del paciente basado en su ID para generar 
    patrones consistentes pero variados entre pacientes.
    """
    import hashlib
    
    # Usar el ID del paciente como semilla para consistencia
    seed = int(hashlib.md5(str(patient_id).encode()).hexdigest()[:8], 16) % 100
    
    # Determinar perfil de salud
    if seed < 25:  # 25% pacientes saludables
        profile_type = "healthy"
    elif seed < 45:  # 20% pacientes sedentarios
        profile_type = "sedentary"
    elif seed < 65:  # 20% pacientes con problemas cardíacos
        profile_type = "cardiac_issues"
    elif seed < 85:  # 20% pacientes con problemas respiratorios
        profile_type = "respiratory_issues"
    else:  # 15% pacientes muy activos
        profile_type = "very_active"
    
    # Configurar perfil base
    profiles = {
        "healthy": {
            "activity_multiplier": 1.0,
            "bpm_modifier": (0, 0),
            "spo2_modifier": (0, 0),
            "daily_target_range": (6000, 12000),
            "pattern_variation": 0.2
        },
        "sedentary": {
            "activity_multiplier": 0.3,
            "bpm_modifier": (-5, 5),
            "spo2_modifier": (0, 0),
            "daily_target_range": (1000, 4000),
            "pattern_variation": 0.1
        },
        "cardiac_issues": {
            "activity_multiplier": 0.7,
            "bpm_modifier": (-15, -5),  # BPM anormalmente bajo
            "spo2_modifier": (0, 0),
            "daily_target_range": (3000, 7000),
            "pattern_variation": 0.3
        },
        "respiratory_issues": {
            "activity_multiplier": 0.8,
            "bpm_modifier": (5, 15),
            "spo2_modifier": (-8, -3),  # SpO2 más bajo
            "daily_target_range": (4000, 8000),
            "pattern_variation": 0.25
        },
        "very_active": {
            "activity_multiplier": 1.5,
            "bpm_modifier": (10, 20),
            "spo2_modifier": (0, 2),
            "daily_target_range": (8000, 15000),
            "pattern_variation": 0.4
        }
    }
    
    base_profile = profiles[profile_type].copy()
    
    # Ajustar según edad
    if age > 65:
        base_profile["activity_multiplier"] *= 0.6
        base_profile["daily_target_range"] = (
            int(base_profile["daily_target_range"][0] * 0.6),
            int(base_profile["daily_target_range"][1] * 0.6)
        )
    elif age < 30:
        base_profile["activity_multiplier"] *= 1.2
        base_profile["daily_target_range"] = (
            int(base_profile["daily_target_range"][0] * 1.1),
            int(base_profile["daily_target_range"][1] * 1.1)
        )
    
    # Ajustar según patologías específicas
    if any("hipertensión" in name for name in pathology_names):
        base_profile["bpm_modifier"] = (
            base_profile["bpm_modifier"][0] + 10,
            base_profile["bpm_modifier"][1] + 20
        )
    
    if any("asma" in name or "bronquitis" in name for name in pathology_names):
        base_profile["spo2_modifier"] = (
            min(base_profile["spo2_modifier"][0] - 5, -8),
            base_profile["spo2_modifier"][1] - 2
        )
    
    if any("artritis" in name or "espalda" in name for name in pathology_names):
        base_profile["activity_multiplier"] *= 0.7
    
    base_profile["profile_type"] = profile_type
    return base_profile

# ── Función para obtener patrones de actividad realistas ───────────────────
def get_realistic_activity_pattern(patient_id: int, age: int, pathology_names: list, health_profile: dict) -> dict:
    """
    Define patrones de actividad por horas del día con variación individual por paciente.
    Cada paciente tiene un patrón único pero realista basado en su perfil de salud.
    """
    import hashlib
    
    # Semilla única por paciente para variación consistente
    patient_seed = int(hashlib.md5(f"{patient_id}_pattern".encode()).hexdigest()[:8], 16)
    random.seed(patient_seed)
    
    # Patrón base más variado
    base_pattern = {
        # Madrugada - sueño (con pequeñas variaciones individuales)
        0: {'intensity': 'sleep', 'steps_per_hour': random.randint(0, 5)},
        1: {'intensity': 'sleep', 'steps_per_hour': random.randint(0, 3)},
        2: {'intensity': 'sleep', 'steps_per_hour': random.randint(0, 2)},
        3: {'intensity': 'sleep', 'steps_per_hour': random.randint(0, 2)},
        4: {'intensity': 'sleep', 'steps_per_hour': random.randint(0, 5)},
        5: {'intensity': 'sleep', 'steps_per_hour': random.randint(0, 10)},
        6: {'intensity': 'sleep', 'steps_per_hour': random.randint(0, 20)},
        
        # Despertar (horarios variables)
        7: {'intensity': 'low', 'steps_per_hour': random.randint(50, 150)},
        
        # Mañana (patrones personalizados)
        8: {'intensity': 'light', 'steps_per_hour': random.randint(150, 300)},
        9: {'intensity': 'light', 'steps_per_hour': random.randint(180, 350)},
        
        # Media mañana
        10: {'intensity': 'moderate', 'steps_per_hour': random.randint(300, 600)},
        11: {'intensity': 'moderate', 'steps_per_hour': random.randint(350, 650)},
        
        # Almuerzo
        12: {'intensity': 'light', 'steps_per_hour': random.randint(150, 300)},
        13: {'intensity': 'light', 'steps_per_hour': random.randint(100, 250)},
        
        # Tarde
        14: {'intensity': 'low', 'steps_per_hour': random.randint(50, 150)},
        15: {'intensity': 'low', 'steps_per_hour': random.randint(30, 120)},
        16: {'intensity': 'low', 'steps_per_hour': random.randint(60, 180)},
        
        # Tarde-noche
        17: {'intensity': 'moderate', 'steps_per_hour': random.randint(250, 500)},
        18: {'intensity': 'moderate', 'steps_per_hour': random.randint(300, 550)},
        19: {'intensity': 'light', 'steps_per_hour': random.randint(200, 400)},
        
        # Noche
        20: {'intensity': 'light', 'steps_per_hour': random.randint(100, 250)},
        21: {'intensity': 'low', 'steps_per_hour': random.randint(50, 150)},
        22: {'intensity': 'low', 'steps_per_hour': random.randint(20, 100)},
        23: {'intensity': 'sleep', 'steps_per_hour': random.randint(0, 30)},
    }
    
    # Resetear seed al estado actual
    random.seed()
    
    # Aplicar multiplicador del perfil de salud
    activity_mult = health_profile["activity_multiplier"]
    variation = health_profile["pattern_variation"]
    
    for hour in base_pattern:
        # Aplicar multiplicador base
        base_pattern[hour]['steps_per_hour'] = int(
            base_pattern[hour]['steps_per_hour'] * activity_mult
        )
        
        # Añadir variación individual
        current_steps = base_pattern[hour]['steps_per_hour']
        variation_amount = int(current_steps * variation * random.uniform(-1, 1))
        base_pattern[hour]['steps_per_hour'] = max(0, current_steps + variation_amount)
    
    # Patrones especiales según perfil
    if health_profile["profile_type"] == "sedentary":
        # Pacientes sedentarios: actividad muy concentrada en pocas horas
        peak_hours = random.sample([10, 11, 17, 18], 2)
        for hour in base_pattern:
            if hour not in peak_hours and hour not in [0, 1, 2, 3, 4, 5, 6, 23]:
                base_pattern[hour]['steps_per_hour'] = int(base_pattern[hour]['steps_per_hour'] * 0.3)
    
    elif health_profile["profile_type"] == "very_active":
        # Pacientes muy activos: múltiples picos de actividad
        for hour in [7, 8, 10, 11, 17, 18, 19]:
            base_pattern[hour]['steps_per_hour'] = int(base_pattern[hour]['steps_per_hour'] * 1.5)
    
    return base_pattern

# ── Función para generar estudios de una hora específica ──────────────────
async def generate_hour_studies(patient_id: int, hour: int, date_base: datetime, 
                               cumulative_steps: int, hour_config: dict, 
                               bpm_range: tuple, spo2_range: tuple, 
                               pathology_names: list, health_profile: dict) -> List[Study]:
    """
    Genera estudios para una hora específica del día siguiendo el patrón de actividad.
    Genera entre 4-12 estudios por hora para alcanzar 300-600 estudios diarios.
    """
    import random
    studies = []
    
    steps_this_hour = hour_config['steps_per_hour']
    intensity = hour_config['intensity']
    
    # Si no hay actividad esta hora, generar pocos estudios con pasos mínimos
    if steps_this_hour == 0:
        # Incluso en horas de sueño, generar algunos estudios para monitoreo
        num_studies = random.randint(1, 2)
        steps_this_hour = random.randint(0, 5)  # Muy pocos pasos durante el sueño
    else:
        # Generar más estudios por hora para llegar a 300-600 diarios
        if intensity == 'sleep':
            num_studies = random.randint(1, 3)
        elif intensity == 'low':
            num_studies = random.randint(3, 6)
        elif intensity == 'light':
            num_studies = random.randint(6, 10)
        elif intensity == 'moderate':
            num_studies = random.randint(8, 12)
        else:
            num_studies = random.randint(4, 8)
    
    # Distribuir los pasos entre los estudios de la hora
    if num_studies > 0:
        steps_per_study = max(1, steps_this_hour // num_studies)
        remaining_steps = steps_this_hour % num_studies
    else:
        return studies
    
    # Generar timestamps ordenados para la hora
    timestamps = []
    for i in range(num_studies):
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        ts = date_base.replace(minute=minutes, second=seconds)
        timestamps.append(ts)
    
    # Ordenar timestamps para mantener secuencia temporal
    timestamps.sort()
    
    # Variable local para rastrear pasos en esta hora
    local_cumulative = cumulative_steps
    
    for i, ts in enumerate(timestamps):
        # Calcular pasos para este estudio (siempre incremental)
        study_steps = steps_per_study
        if i < remaining_steps:
            study_steps += 1
        
        # CRÍTICO: Los pasos son siempre acumulativos (nunca decrece)
        local_cumulative += study_steps
        
        # Ajustar BPM según intensidad y perfil de salud
        bpm_base = bpm_range[0] + int((bpm_range[1] - bpm_range[0]) * 0.3)
        bpm_mod = health_profile["bpm_modifier"]
        
        if intensity == 'moderate':
            bpm = random.randint(
                max(50, bpm_base + 10 + bpm_mod[0]), 
                min(150, bpm_range[1] + bpm_mod[1])
            )
        elif intensity == 'light':
            bpm = random.randint(
                max(50, bpm_base + bpm_mod[0]), 
                min(150, bpm_base + 15 + bpm_mod[1])
            )
        elif intensity == 'sleep':
            bpm = random.randint(
                max(40, bpm_range[0] + bpm_mod[0]), 
                max(50, bpm_base + bpm_mod[1])
            )
        else:  # low
            bpm = random.randint(
                max(50, bpm_range[0] + bpm_mod[0]), 
                max(60, bpm_base + 5 + bpm_mod[1])
            )
        
        # SpO2 con variaciones según perfil de salud
        spo2_mod = health_profile["spo2_modifier"]
        spo2 = random.randint(
            max(85, spo2_range[0] + spo2_mod[0]), 
            min(100, spo2_range[1] + spo2_mod[1])
        )
        
        # Ocasionalmente generar valores anómalos según perfil
        if random.random() < 0.05:  # 5% de lecturas anómalas
            if health_profile["profile_type"] == "cardiac_issues":
                bpm = random.randint(35, 50)  # Bradicardia
            elif health_profile["profile_type"] == "respiratory_issues":
                spo2 = random.randint(85, 92)  # Hipoxemia
            elif any("hipertensión" in name for name in pathology_names):
                bpm = random.randint(110, 140)  # Crisis hipertensiva
        
        study = await StudyCtrl.create(
            Study.CreateValidator(
                patient_id = patient_id,
                step_count = local_cumulative,  # Usar variable local
                bpm        = bpm,
                spo2       = spo2,
                ts         = ts
            ),
            validate         = False,
            with_transaction = False
        )
        studies.append(study)
    
    return studies

# ── Función que genera las lecturas de un solo día para un paciente ───────────
async def _generate_daily_studies(patient_id: int, start_ts: datetime, end_ts: datetime, is_most_recent_day: bool = False) -> List[Study]:
    """
    Crea lecturas (Study) para un paciente entre start_ts y end_ts (ambos naïve datetimes),
    con patrones de actividad realistas:
      - El acumulado de 'step_count' empiece en 0 ese día.
      - Los valores de step_count son SIEMPRE incrementales (nunca decrece).
      - Patrones de actividad realistas con horas pico y períodos de descanso.
      - Los valores vitales son más realistas según la edad y patologías del paciente.
      - Genera entre 300-600 estudios por día según el perfil del paciente.
    """
    import random
    studies = []
    
    # Obtener información del paciente para personalizar los valores
    patient = await PatientCtrl.get(patient_id)
    patient_pathologies_result = await PatientPathologyCtrl.search(
        extra_args={'patient_id': patient_id}
    )
    patient_pathologies = patient_pathologies_result[0]  # El método search devuelve (records, has_more)
    pathology_names = [pp.pathology.name.lower() if pp.pathology else "" for pp in patient_pathologies]
    
    # Calcular edad
    birth_year = patient.birth_date.year
    current_year = datetime.now().year
    age = current_year - birth_year
    
    # Obtener perfil de salud del paciente
    health_profile = get_patient_health_profile(patient_id, age, pathology_names)
    
    # Ajustar rangos de valores según edad y patologías
    if age > 65:
        base_bpm_range = (65, 85)
        base_spo2_range = (92, 98)
    elif age > 45:
        base_bpm_range = (65, 90)
        base_spo2_range = (95, 100)
    else:
        base_bpm_range = (60, 95)
        base_spo2_range = (96, 100)
    
    # Aplicar modificadores del perfil de salud
    bpm_mod = health_profile["bpm_modifier"]
    spo2_mod = health_profile["spo2_modifier"]
    
    bpm_range = (
        max(40, base_bpm_range[0] + bpm_mod[0]),
        min(150, base_bpm_range[1] + bpm_mod[1])
    )
    spo2_range = (
        max(85, base_spo2_range[0] + spo2_mod[0]),
        min(100, base_spo2_range[1] + spo2_mod[1])
    )
    
    # Obtener objetivo diario del perfil
    daily_target_steps = random.randint(
        health_profile["daily_target_range"][0],
        health_profile["daily_target_range"][1]
    )
    
    # Configurar patrones de actividad por horas del día
    activity_patterns = get_realistic_activity_pattern(patient_id, age, pathology_names, health_profile)
    
    # Generar estudios siguiendo el patrón de actividad
    cumulative_steps = 0
    all_hour_studies = []
    
    # Procesar cada hora desde start hasta end
    current_hour = start_ts.hour
    while current_hour <= end_ts.hour:
        # Obtener configuración para esta hora
        hour_config = activity_patterns.get(current_hour, {'intensity': 'low', 'steps_per_hour': 50})
        
        # Generar lecturas para esta hora
        hour_studies = await generate_hour_studies(
            patient_id=patient_id,
            hour=current_hour,
            date_base=start_ts.replace(hour=current_hour, minute=0, second=0),
            cumulative_steps=cumulative_steps,
            hour_config=hour_config,
            bpm_range=bpm_range,
            spo2_range=spo2_range,
            pathology_names=pathology_names,
            health_profile=health_profile
        )
        
        # Actualizar pasos acumulados con el último estudio de la hora
        if hour_studies:
            # Importante: tomar el último valor de pasos de la hora
            cumulative_steps = hour_studies[-1].step_count
            all_hour_studies.extend(hour_studies)
        
        current_hour += 1
    
    # Ordenar todos los estudios por timestamp para mantener secuencia
    all_hour_studies.sort(key=lambda x: x.ts)
    
    # CRÍTICO: Recalcular step_count para asegurar progresión incremental
    # después del ordenamiento por timestamp
    current_steps = 0
    for study in all_hour_studies:
        # Los pasos deben ser siempre incrementales después del ordenamiento
        if study.step_count <= current_steps:
            study.step_count = current_steps + random.randint(1, 15)
        current_steps = study.step_count
    
    studies.extend(all_hour_studies)
    
    # Si no hemos alcanzado el objetivo diario, ajustar gradualmente
    # pero NO agregar un estudio final que rompa la secuencia temporal
    if cumulative_steps < daily_target_steps and all_hour_studies:
        steps_needed = daily_target_steps - cumulative_steps
        
        # Si la diferencia es razonable, distribuir entre los últimos estudios
        if steps_needed <= 500 and len(all_hour_studies) > 0:
            # Distribuir los pasos faltantes entre los últimos estudios
            last_studies = all_hour_studies[-min(3, len(all_hour_studies)):]
            extra_per_study = steps_needed // len(last_studies)
            
            for i, study in enumerate(last_studies):
                additional_steps = extra_per_study
                if i < steps_needed % len(last_studies):
                    additional_steps += 1
                study.step_count += additional_steps
        
        # Si la diferencia es muy grande, simplemente ajustar el objetivo
        elif steps_needed > 500:
            daily_target_steps = cumulative_steps

    return studies


# ── Función para generar alarmas ───────────────────────────────────────────────
async def seed_alarms_for_patients(patients):
    print(" -- seeding alarms for patients")
    alarms = []
    types = ['fall_detected', 'strange_bpm', 'button_alarm']
    
    for patient in patients:
        # Obtener las patologías del paciente para generar alarmas más específicas
        patient_pathologies_result = await PatientPathologyCtrl.search(
            extra_args={'patient_id': patient.id}
        )
        patient_pathologies = patient_pathologies_result[0]  # El método search devuelve (records, has_more)
        pathology_names = [pp.pathology.name.lower() if pp.pathology else "" for pp in patient_pathologies]
        
        # Ajustar probabilidad de alarmas según patologías
        num_alarms = random.randint(0, 2)  # Reducido de (1,5) a (1,2)
        
        # Pacientes con condiciones cardíacas tienen más probabilidad de alarmas de BPM
        if any("hipertensión" in name or "diabetes" in name for name in pathology_names):
            if random.random() < 0.8:  # Aumentado de 60% a 80%
                num_alarms += random.randint(0, 1)  # Reducido: máximo 1 alarma adicional
                types_weighted = ['strange_bpm'] * 4 + ['button_alarm'] + ['fall_detected']
            else:
                types_weighted = types
        # Pacientes mayores tienen más probabilidad de caídas
        elif any("avanzada edad" in name or "artritis" in name or "osteoporosis" in name for name in pathology_names):
            if random.random() < 0.7:  # Aumentado de 40% a 70%
                num_alarms += random.randint(0, 1)  # Reducido: máximo 1 alarma adicional
                types_weighted = ['fall_detected'] * 3 + ['strange_bpm'] + ['button_alarm']
            else:
                types_weighted = types
        else:
            # Incluso pacientes sin patologías específicas pueden tener algunas alarmas
            if random.random() < 0.1:
                # No añadir alarmas adicionales para mantener el rango bajo
                pass
            types_weighted = types
        
        for _ in range(num_alarms):
            # alarm_ts debe ser naive, pero más reciente y realista
            days_ago = random.randint(0, 30)  # Últimos 30 días
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            alarm_ts = (datetime.now(timezone.utc) - timedelta(
                days=days_ago, 
                hours=hours_ago, 
                minutes=minutes_ago
            )).replace(tzinfo=None)
            
            alarm_type = random.choice(types_weighted)
            
            # Alarmas de caída y botón de pánico son más urgentes
            is_urgent = alarm_type in ['fall_detected', 'button_alarm'] or random.choice([True, False])
            
            alarm = await AlarmCtrl.create(
                Alarm.CreateValidator(
                    patient_id = patient.id,
                    alarm_type = alarm_type,
                    ts         = alarm_ts,
                    is_urgent  = is_urgent
                ),
                validate         = False,
                with_transaction = False
            )
            alarms.append(alarm)
    
    return alarms



async def seed_messages_for_chat(chat, user_a, user_b):
    """
    Inserta conversaciones realistas entre médico y paciente.
    Las conversaciones siguen patrones típicos de consultas médicas.
    """
    import random
    
    # Conversaciones predefinidas típicas de consultas médicas
    MEDICAL_CONVERSATIONS = [
        [
            "Buenos días, tengo que hacerte una consulta",
            "Claro, dime en qué te puedo ayudar",
            "He notado que mis datos han estado un poco raros últimamente. ¿podríamos revisar el equipo?",
            "Veo en tus datos que efectivamente has tenido algunos valores extraños. ¿Has sentido algún malestar?",
            "Un poco de cansancio, pero nada más",
            "Te recomiendo que mantengas un registro de cómo te sientes cuando notes esas subidas y te agendaré una cita para el lunes"
        ],
        [
            "Doctor, ¿podría revisar mis datos de esta semana?",
            "Por supuesto. Veo que has estado muy activo, felicidades",
            "Gracias, he estado siguiendo sus recomendaciones",
            "Perfecto, mantén ese ritmo de ejercicio"
        ],
        [
            "Hola doctor, tengo una duda sobre la medicación",
            "Dime, ¿qué necesitas saber?",
            "¿Puedo tomar la pastilla antes o después de las comidas?",
            "Es mejor tomarla con las comidas para evitar molestias estomacales",
            "Perfecto, muchas gracias"
        ],
        [
            "Buenos días",
            "Hola, ¿cómo te encuentras hoy?",
            "Bastante bien, gracias por preguntar",
            "Me alegra saberlo. Recuerda hacer los ejercicios que te recomendé"
        ],
        [
            "Doctor, me he saltado la medicación dos días",
            "No te preocupes, pero es importante que mantengas la constancia",
            "Lo sé, se me olvidó. ¿Debo tomar doble dosis ahora?",
            "No, continúa con la pauta normal. Te sugiero poner una alarma",
            "Buena idea, lo haré"
        ],

        # NUEVAS CONVERSACIONES

        # Paciente quiere agendar cita, doctor sugiere otros medios
        [
            "Doctor, me gustaría agendar una cita para la próxima semana",
            "Claro, puedo hacerlo por aquí, aunque también puedes usar la app o llamar al centro, es más rápido",
            "Soy bastante malo con la tecnología, pero por este chat me resulta mucho más fácil",
            "Perfecto, entonces te agendo por aquí. La tienes para el martes a las 10:00"
        ],

        # Pulsera detecta caídas falsamente
        [
            "Doctor, mi pulsera está mostrando que detectó una caída, pero no me pasó nada",
            "Entiendo, puede ser una falsa detección. ¿Ha ocurrido varias veces?",
            "Sí, unas tres veces esta semana",
            "Voy a pedir que se le haga un nuevo ajuste al dispositivo para evitar falsas alarmas"
        ],

        # Paciente pide cambio de batería en dispositivo
        [
            "Buenos días doctor, mi dispositivo se descarga muy rápido",
            "Podría ser que la batería esté fallando. ¿Cuánto dura ahora?",
            "Menos de medio día",
            "Solicitaré un reemplazo de batería para que lo tengas funcionando correctamente"
        ],

        # Paciente pregunta por datos de sueño
        [
            "Doctor, ¿puede revisar mis datos de sueño?",
            "Sí, veo que esta semana has dormido menos horas que la anterior",
            "Es cierto, he tenido mucho trabajo",
            "Te recomiendo que intentes recuperar horas de descanso este fin de semana"
        ],

        # Paciente pide revisión de presión arterial
        [
            "Hola doctor, creo que mi presión arterial está más alta de lo normal",
            "Revisando... sí, tus registros muestran valores un poco elevados",
            "¿Debo preocuparme?",
            "Por ahora no es grave, pero haré que te vea un especialista en los próximos días"
        ],

        # Paciente reporta dolor
        [
            "Doctor, he tenido dolor en el pecho desde ayer",
            "¿Es un dolor punzante o más bien presión?",
            "Más bien como presión, especialmente cuando camino",
            "Es importante que vengas a consulta hoy mismo, voy a hacer un hueco en mi agenda"
        ],

        # Consulta sobre ejercicio
        [
            "¿Cuánto ejercicio debo hacer según mis datos?",
            "Veo que has estado caminando poco esta semana",
            "Es que me duelen las rodillas",
            "Entiendo, mejor empecemos con ejercicios de bajo impacto como natación"
        ],

        # Problema con la app
        [
            "Doctor, no puedo ver mis datos en la aplicación",
            "¿Has intentado cerrar y abrir la app otra vez?",
            "Sí, varias veces, pero sigue igual",
            "Te voy a pasar con soporte técnico para que te ayuden"
        ],

        # Consulta sobre dieta
        [
            "¿Mis niveles de glucosa están bien?",
            "Están un poco altos, ¿has estado siguiendo la dieta?",
            "Sí, pero ayer fue mi cumpleaños...",
            "No pasa nada por un día especial, pero vamos a ajustar la medicación por unos días"
        ]
    ]

    mensajes = []
    # Empezamos hace un día (naive datetime) para simular conversación reciente
    ts = (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 7))).replace(tzinfo=None)
    
    # Seleccionamos una conversación aleatoria
    conversation = random.choice(MEDICAL_CONVERSATIONS)
    
    # El primer mensaje siempre es del user_b (paciente), el segundo del user_a (doctor)
    is_patient_turn = True
    
    for i, content in enumerate(conversation):
        # Avanzamos entre 1 y 30 minutos entre mensajes para simular tiempo de respuesta real
        if i > 0:
            ts += timedelta(minutes=random.randint(1, 30))
        
        sender = user_b if is_patient_turn else user_a
        
        msg = await MessageCtrl.create(
            Message.CreateValidator(
                chat_id   = chat.id,
                sender_id = sender.id,
                content   = content,
                ts        = ts
            ),
            validate         = False,
            with_transaction = False
        )
        mensajes.append(msg)
        
        # Alternamos entre paciente y doctor
        is_patient_turn = not is_patient_turn

    return mensajes


async def chat_exists(user1_id, user2_id):
    chats, _ = await ChatCtrl.search()
    for c in chats:
        if (c.user1_id == user1_id and c.user2_id == user2_id) or \
           (c.user1_id == user2_id and c.user2_id == user1_id):
            return True
    return False

async def seed_realistic_chats(admin_users: List[UserAccount], doctors: List[UserAccount], all_demo_patients: List[Patient]):
    print(" -- Creating realistic chat system")
    chats_creados = []
    mensajes_creados = []

    admin_id = admin_users[0].id

    # 1) Admin <-> doctores
    for doctor in doctors:
        if await chat_exists(admin_id, doctor.id):
            print(f"Chat ya existe entre admin y doctor {doctor.id}")
            continue
        try:
            chat = await ChatCtrl.create(
                Chat.CreateValidator(
                    user1_id = admin_id,
                    user2_id = doctor.id,
                    administration = True
                ),
                validate         = False,
                with_transaction = False
            )
            chats_creados.append(chat)
            if random.random() > 0.2:
                msgs = await seed_admin_messages_for_chat(chat, admin_id, doctor.id)
                mensajes_creados.extend(msgs)
        except Exception as e:
            print(f"Error creando chat admin-doctor: {e}")

    # 2) Admin <-> pacientes
    for patient in all_demo_patients:
        patient_user_id = getattr(patient, 'patient_user_account', None)
        if patient_user_id:
            patient_user_id = patient_user_id.id
        else:
            patient_user_id = patient.owner_user_id
        if await chat_exists(admin_id, patient_user_id):
            print(f"Chat ya existe entre admin y paciente {patient_user_id}")
            continue
        try:
            chat = await ChatCtrl.create(
                Chat.CreateValidator(
                    user1_id = admin_id,
                    user2_id = patient_user_id,
                    administration = True
                ),
                validate         = False,
                with_transaction = False
            )
            chats_creados.append(chat)
            msgs = await seed_admin_patient_messages_for_chat(chat, admin_id, patient_user_id)
            mensajes_creados.extend(msgs)
        except Exception as e:
            print(f"Error creando chat admin-paciente: {e}")

    # 3) Doctor <-> paciente
    for patient in all_demo_patients:
        if hasattr(patient, 'assigned_doctor_id'):
            doctor_id = patient.assigned_doctor_id
            patient_user_id = getattr(patient, 'patient_user_account', None)
            if patient_user_id:
                patient_user_id = patient_user_id.id
            else:
                patient_user_id = patient.owner_user_id
            if await chat_exists(doctor_id, patient_user_id):
                print(f"Chat ya existe entre doctor {doctor_id} y paciente {patient_user_id}")
                continue
            try:
                chat = await ChatCtrl.create(
                    Chat.CreateValidator(
                        user1_id = doctor_id,
                        user2_id = patient_user_id,
                        administration = False
                    ),
                    validate         = False,
                    with_transaction = False
                )
                chats_creados.append(chat)
                if random.random() > 0.3:
                    from types import SimpleNamespace
                    user_doctor = SimpleNamespace(id = doctor_id)
                    user_patient = SimpleNamespace(id = patient_user_id)
                    msgs = await seed_messages_for_chat(chat, user_doctor, user_patient)
                    mensajes_creados.extend(msgs)
            except Exception as e:
                print(f"Error creando chat médico: {e}")

    # 4) Doctor <-> colega
    for i, doctor1 in enumerate(doctors):
        num_colleagues = random.randint(1, min(3, len(doctors) - 1))
        possible_colleagues = [d for d in doctors if d.id != doctor1.id]
        colleagues = random.sample(possible_colleagues, min(num_colleagues, len(possible_colleagues)))
        for doctor2 in colleagues:
            if doctor1.id < doctor2.id:
                if await chat_exists(doctor1.id, doctor2.id):
                    print(f"Chat ya existe entre doctor {doctor1.id} y colega {doctor2.id}")
                    continue
                try:
                    chat = await ChatCtrl.create(
                        Chat.CreateValidator(
                            user1_id = doctor1.id,
                            user2_id = doctor2.id,
                            administration = False
                        ),
                        validate         = False,
                        with_transaction = False
                    )
                    chats_creados.append(chat)
                    if random.random() > 0.4:
                        msgs = await seed_colleague_messages_for_chat(chat, doctor1.id, doctor2.id)
                        mensajes_creados.extend(msgs)
                except Exception as e:
                    print(f"Error creando chat entre colegas: {e}")

    print(f" -- Se crearon {len(chats_creados)} chats realistas "
          f"y {len(mensajes_creados)} mensajes en total")
    return chats_creados, mensajes_creados


async def seed_admin_messages_for_chat(chat, admin_id, doctor_id):
    """Mensajes típicos entre admin y doctores"""
    ADMIN_DOCTOR_CONVERSATIONS = [
        [
            "Hola, necesito que revises el nuevo protocolo de seguimiento",
            "Por supuesto, ¿cuándo lo necesitas implementado?",
            "Preferiblemente antes del viernes",
            "Perfecto, lo tendré listo"
        ],
        [
            "¿Cómo van los pacientes nuevos de esta semana?",
            "Bastante bien, hemos incorporado 3 nuevos pacientes",
            "Excelente, mantén el buen trabajo"
        ],
        [
            "Reunión de equipo el martes a las 15:00",
            "Anotado, ¿algún tema específico?",
            "Revisaremos las estadísticas mensuales",
            "Perfecto, llevaré los informes preparados"
        ]
    ]
    
    conversation = random.choice(ADMIN_DOCTOR_CONVERSATIONS)
    mensajes = []
    ts = (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 5))).replace(tzinfo=None)
    
    # Admin siempre inicia la conversación
    is_admin_turn = True
    
    for i, content in enumerate(conversation):
        if i > 0:
            ts += timedelta(minutes=random.randint(5, 60))
        
        sender_id = admin_id if is_admin_turn else doctor_id
        
        msg = await MessageCtrl.create(
            Message.CreateValidator(
                chat_id   = chat.id,
                sender_id = sender_id,
                content   = content,
                ts        = ts
            ),
            validate         = False,
            with_transaction = False
        )
        mensajes.append(msg)
        is_admin_turn = not is_admin_turn
    
    return mensajes


async def seed_admin_patient_messages_for_chat(chat, admin_id, patient_id):
    """Mensajes típicos entre admin y pacientes"""
    ADMIN_PATIENT_CONVERSATIONS = [
        [
            "Hola, bienvenido al sistema de seguimiento médico",
            "Muchas gracias, ¿cómo funciona exactamente?",
            "Tu doctor recibirá todos los datos de tu pulsera automáticamente",
            "Perfecto, eso me tranquiliza mucho"
        ],
        [
            "Recordatorio: tienes cita médica programada para el próximo lunes",
            "Gracias por recordármelo",
            "¿Necesitas cambiar la hora?",
            "No, la hora está perfecta"
        ]
    ]
    
    conversation = random.choice(ADMIN_PATIENT_CONVERSATIONS)
    mensajes = []
    ts = (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 7))).replace(tzinfo=None)
    
    is_admin_turn = True
    
    for i, content in enumerate(conversation):
        if i > 0:
            ts += timedelta(minutes=random.randint(10, 120))
        
        sender_id = admin_id if is_admin_turn else patient_id
        
        msg = await MessageCtrl.create(
            Message.CreateValidator(
                chat_id   = chat.id,
                sender_id = sender_id,
                content   = content,
                ts        = ts
            ),
            validate         = False,
            with_transaction = False
        )
        mensajes.append(msg)
        is_admin_turn = not is_admin_turn
    
    return mensajes


async def seed_colleague_messages_for_chat(chat, doctor1_id, doctor2_id):
    """Mensajes típicos entre doctores colegas"""
    COLLEAGUE_CONVERSATIONS = [
        [
            "¿Has visto los nuevos protocolos de cardiología?",
            "Sí, son bastante completos",
            "¿Qué opinas sobre la sección de arritmias?",
            "Muy detallada, me parece una gran mejora"
        ],
        [
            "Consulta: ¿has tratado casos de hipertensión resistente?",
            "Varios, ¿qué necesitas saber?",
            "Protocolos de medicación combinada",
            "Te paso un artículo muy bueno sobre el tema"
        ],
        [
            "¿Vienes a la conferencia del viernes?",
            "Claro, ¿de qué tema hablan?",
            "Nuevas tecnologías en monitoreo remoto",
            "Perfecto, nos vemos allí"
        ]
    ]
    
    conversation = random.choice(COLLEAGUE_CONVERSATIONS)
    mensajes = []
    ts = (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10))).replace(tzinfo=None)
    
    is_doctor1_turn = True
    
    for i, content in enumerate(conversation):
        if i > 0:
            ts += timedelta(minutes=random.randint(15, 180))
        
        sender_id = doctor1_id if is_doctor1_turn else doctor2_id
        
        msg = await MessageCtrl.create(
            Message.CreateValidator(
                chat_id   = chat.id,
                sender_id = sender_id,
                content   = content,
                ts        = ts
            ),
            validate         = False,
            with_transaction = False
        )
        mensajes.append(msg)
        is_doctor1_turn = not is_doctor1_turn
    
    return mensajes



# noinspection PyShadowingNames
async def main(
        db_url        : str,
        open_db       : bool = True,
        close_db      : bool = True,
        is_production : bool = False
):
    seed_type = "production" if is_production else "development"
    print(f"** Start {seed_type} seeding **")

    # init/connect db
    database_manager.init(db_url)
    if open_db:
        await database_manager.open()

    # 1) Common entities
    async with database_manager.get_db_conn().transaction():
        await asyncio.gather(
            seed_user_roles(),
            seed_user_statuses(),
            seed_gender_types(),
            seed_permissions(),
        )

    # 2) Required entities (admin, pathologies, instruments, skip studies)
    async with database_manager.get_db_conn().transaction():
        admin, pathologies, _ = await asyncio.gather(
            seed_admin_user(),
            seed_pathologies(),
            seed_instruments(),
        )

    # 3) Demo data: demo users, pacientes, chats, estudios y alarmas
    async with database_manager.get_db_conn().transaction():
        demo_doctors = await seed_demo_users()
        demo_patients = []
        for doctor in demo_doctors:
            # Si es doctor@bracelet.com, darle 55 pacientes
            if doctor.email == "doctor@bracelet.com":
                print(f" -- Creating 55 patients for doctor@bracelet.com (doctor id: {doctor.id})")
                for _ in range(55):
                    patient = await create_single_patient_with_doctor(doctor.id, pathologies)
                    demo_patients.append(patient)
            else:
                # Para otros doctores, usar el rango normal
                demo_patients.extend(await seed_patients(doctor.id, pathologies))

        # Paciente especial para el TFG - asignado al primer doctor
        if demo_doctors:
            ejemplo_patient = await create_single_patient_account_with_doctor(
                email       = "paciente@bracelet.com",
                password    = "TFGde10",
                first_name  = "Diego",
                last_name   = "De Pablo",
                phone       = "+34 674 555 555",
                gender      = "male",
                weight      = 53,
                birth_date  = date(2002, 5, 6),
                assigned_doctor_id = demo_doctors[0].id,
                user_status = "active"
            )
        else:
            ejemplo_patient = await create_single_patient_account(
                email       = "paciente@bracelet.com",
                password    = "TFGde10",
                first_name  = "Diego",
                last_name   = "De Pablo",
                phone       = "+34 674 555 555",
                gender      = "male",
                weight      = 53,
                birth_date  = date(2002, 5, 6),
                user_status = "active"
            )
        print(f" -- Patient account: UserAccount.id={ejemplo_patient.patient_user_account.id if hasattr(ejemplo_patient, 'patient_user_account') else ejemplo_patient.owner_user_id}, Patient.id={ejemplo_patient.id}")

        # Crear pacientes de ejemplo con casos típicos
        # Asignar a doctores aleatorios de la lista
        example_patients = await create_example_patients(pathologies, demo_doctors)
        print(f" -- Created {len(example_patients)} example patients with specific medical cases")

        # Crear pacientes adicionales con cuentas de usuario (rol patient)
        patient_user_accounts = await seed_patient_user_accounts(pathologies, num_new_patient_users)
        print(f" -- Created {len(patient_user_accounts)} patient user accounts")

        # Añadimos todos los pacientes a la lista para asegurar que tengan estudios
        all_demo_patients = demo_patients + [ejemplo_patient] + example_patients + patient_user_accounts

        # Generamos estudios para TODOS los pacientes demo
        print(f" -- Generating studies for {len(all_demo_patients)} patients (this may take a few minutes)")
        await seed_studies_for_patients(all_demo_patients)
        await seed_alarms_for_patients(all_demo_patients)

        # Crear sistema de chats realista
        admin_users = [admin]  # Lista de admins
        await seed_realistic_chats(admin_users, demo_doctors, all_demo_patients)

 

    # 4) Development data (solo si no es producción)
    if not is_production:
        async with database_manager.get_db_conn().transaction():
            dev_doctors = await seed_users()
            dev_patients = []
            for doctor in dev_doctors:
                dev_patients.extend(await seed_patients(doctor.id, pathologies))
            
            # Aseguramos que los pacientes de desarrollo también tengan estudios
            print(f" -- Generating studies for {len(dev_patients)} development patients (this may take a few minutes)")
            await seed_studies_for_patients(dev_patients)
            await seed_alarms_for_patients(dev_patients)
            
            # Crear chats también para el entorno de desarrollo
            admin_users = [admin]
            await seed_realistic_chats(admin_users, dev_doctors, dev_patients)

    if close_db:
        await database_manager.close()

    print("** Finished seeding **")
    print("\n=== RESUMEN DE DATOS CREADOS ===")
    print("✅ Roles, estados y permisos del sistema")
    print("✅ Usuario admin y patologías base")
    print("✅ 4 doctores demo + pacientes asignados")
    print("✅ 3 pacientes de ejemplo con casos específicos")
    print(f"✅ {num_new_patient_users} cuentas de pacientes adicionales")
    print("✅ Estudios médicos para todos los pacientes")
    print("✅ Alarmas personalizadas según patologías")
    print("✅ Sistema de chats jerárquico realista")
    if not is_production:
        print("✅ Datos de desarrollo adicionales")
    print("\n🎯 TU SISTEMA ESTÁ LISTO PARA DEMOSTRAR!")
    print("🔑 Credenciales principales:")
    print("   - Admin: admin@bracelet.com / TFGde10")
    print("   - Paciente TFG: paciente@bracelet.com / TFGde10")
    print("   - Doctores: doctor@bracelet.com, doctor2@bracelet.com, etc. / TFGde10")
    print("   - Pacientes: maria.garcia@email.com, carlos.lopez@email.com, etc. / TFGde10")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="seed.py", description="Initial BD seeding for bracelet API")
    parser.add_argument("-p", "--prod", dest="production", action="store_true", help="Enable production mode")

    args = parser.parse_args()

    db_url = os.getenv("API_DB_URL")
    if db_url is None:
        print("You need to set API_DB_URL environment, exiting...")
        sys.exit(1)

    asyncio.run( main(db_url=db_url, is_production=args.production) )

import { useEffect, useState } from "react";
import { api } from "./api";

const emptyRegistration = {
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  date_of_birth: "",
  sex_at_birth: "",
  phone: "",
  country: "United States",
  state: "",
  city: "",
  postal_code: "",
};

const EDITABLE_PROFILE_FIELDS = [
  "first_name", "last_name", "date_of_birth", "sex_at_birth", "phone",
  "country", "state", "city", "postal_code", "preferred_language",
];

const LANGUAGE_OPTIONS = [
  "English", "Spanish", "French", "Mandarin Chinese", "Cantonese",
  "Vietnamese", "Tagalog", "Arabic", "Korean", "Russian", "Haitian Creole",
  "Portuguese", "German", "Hindi", "Urdu", "Bengali", "Punjabi",
  "Japanese", "Polish", "Somali", "Swahili", "Amharic",
];

const SERVICES = [
  { id: "directory", label: "Find a doctor or facility", blurb: "Search active providers and healthcare facilities by city or specialty." },
  { id: "concern", label: "Find care for a health concern", blurb: "Pick the type of issue and we will point you to the matching specialty." },
  { id: "profile", label: "Manage my profile and preferences", blurb: "Update your contact details and preferred language." },
];

const CONCERN_TO_SPECIALTY = [
  { label: "General checkup or a common illness", specialty: "PRIMARY_CARE" },
  { label: "Heart, blood pressure, or circulation", specialty: "CARDIOLOGY" },
  { label: "Skin, hair, or nails", specialty: "DERMATOLOGY" },
  { label: "Bones, joints, or a recent injury", specialty: "ORTHOPEDICS" },
  { label: "Children's health", specialty: "PEDIATRICS" },
  { label: "Mental health or counseling", specialty: "BEHAVIORAL_HEALTH" },
  { label: "Pregnancy or reproductive health", specialty: "OBSTETRICS_GYNECOLOGY" },
  { label: "Diabetes, thyroid, or hormones", specialty: "ENDOCRINOLOGY" },
  { label: "Stomach or digestive problems", specialty: "GASTROENTEROLOGY" },
  { label: "Eyes or vision", specialty: "OPHTHALMOLOGY" },
];

function Notice({ message, kind = "info" }) {
  if (!message) return null;
  return <div className={`notice ${kind}`} role="status">{message}</div>;
}

function Landing({ setView }) {
  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">Care navigation, made human</span>
          <h1>Find the right care with confidence.</h1>
          <p>
            ZambeCare connects patients with doctors and facilities while keeping privacy,
            reliability, and understandable health information at the center.
          </p>
          <div className="actions">
            <button className="primary" onClick={() => setView("register")}>Create patient account</button>
            <button className="secondary" onClick={() => setView("directory")}>Explore care directory</button>
          </div>
          <small>Demonstration environment — synthetic patient information only.</small>
        </div>
        <div className="hero-card">
          <div className="pulse">Z</div>
          <h2>Your health journey, organized</h2>
          <ul>
            <li><span>01</span> Secure patient profile</li>
            <li><span>02</span> Doctor and facility search</li>
            <li><span>03</span> Clinical data foundation</li>
          </ul>
        </div>
      </section>
      <section className="feature-grid">
        <article><b>Private by design</b><p>Role-based access, secure sessions, and auditable activity.</p></article>
        <article><b>Built for access</b><p>Search active doctors and facilities by the care you need.</p></article>
        <article><b>Ready to grow</b><p>A foundation for referrals, monitoring, analytics, and safe AI routing.</p></article>
      </section>
    </main>
  );
}

function Register({ setView }) {
  const [form, setForm] = useState(emptyRegistration);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });
  const submit = async (event) => {
    event.preventDefault();
    setBusy(true); setMessage("");
    try {
      await api.register({
        ...form,
        sex_at_birth: form.sex_at_birth || null,
        phone: form.phone || null,
        state: form.state || null,
        city: form.city || null,
        postal_code: form.postal_code || null,
      });
      setView("login");
    } catch (error) { setMessage(error.message); }
    finally { setBusy(false); }
  };
  return (
    <main className="panel-wrap">
      <form className="panel form" onSubmit={submit}>
        <span className="eyebrow">New patient</span><h1>Create your account</h1>
        <Notice message={message} kind="error" />
        <div className="form-grid">
          <label>First name<input name="first_name" value={form.first_name} onChange={update} required /></label>
          <label>Last name<input name="last_name" value={form.last_name} onChange={update} required /></label>
          <label className="wide">Email<input name="email" type="email" value={form.email} onChange={update} required /></label>
          <label className="wide">Password<input name="password" type="password" minLength="12" value={form.password} onChange={update} required /><small>12+ characters with upper, lower, number, and symbol.</small></label>
          <label>Date of birth<input name="date_of_birth" type="date" value={form.date_of_birth} onChange={update} required /></label>
          <label>Sex at birth<select name="sex_at_birth" value={form.sex_at_birth} onChange={update}><option value="">Prefer not to answer</option><option>FEMALE</option><option>MALE</option><option>INTERSEX</option></select></label>
          <label className="wide">Phone (optional)<input name="phone" value={form.phone} onChange={update} /></label>
          <label>Country<input name="country" value={form.country} onChange={update} /></label>
          <label>State / Region (optional)<input name="state" value={form.state} onChange={update} /></label>
          <label>City (optional)<input name="city" value={form.city} onChange={update} /></label>
          <label>ZIP / Postal code (optional)<input name="postal_code" value={form.postal_code} onChange={update} /></label>
        </div>
        <small>Address is optional and helps us show doctors and facilities near you. You can add or change it later from your profile.</small>
        <button className="primary full" disabled={busy}>{busy ? "Creating account…" : "Create account"}</button>
      </form>
    </main>
  );
}

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const submit = async (event) => {
    event.preventDefault(); setMessage("");
    try { onLogin(await api.login({ email, password })); }
    catch (error) { setMessage(error.message); }
  };
  return (
    <main className="panel-wrap compact">
      <form className="panel form" onSubmit={submit}>
        <span className="eyebrow">Welcome back</span><h1>Patient sign in</h1>
        <Notice message={message} kind="error" />
        <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        <button className="primary full">Sign in securely</button>
      </form>
    </main>
  );
}

function toQuery(params) {
  const parts = Object.entries(params)
    .filter(([, value]) => value)
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`);
  return parts.length ? `?${parts.join("&")}` : "";
}

function Directory({ initialCity = "", initialState = "", initialSpecialty = "" }) {
  const [facilities, setFacilities] = useState([]);
  const [providers, setProviders] = useState([]);
  const [city, setCity] = useState(initialCity);
  const [stateRegion, setStateRegion] = useState(initialState);
  const [specialty, setSpecialty] = useState(initialSpecialty);
  const [message, setMessage] = useState("");
  const search = async () => {
    setMessage("");
    try {
      const [facilityData, providerData] = await Promise.all([
        api.facilities(toQuery({ city, state: stateRegion })),
        api.providers(toQuery({ specialty, city, state: stateRegion })),
      ]);
      setFacilities(facilityData); setProviders(providerData);
    } catch (error) { setMessage(error.message); }
  };
  useEffect(() => { search(); }, []);
  return (
    <main className="directory">
      <span className="eyebrow">Care directory</span><h1>Doctors and facilities</h1>
      <div className="search-bar">
        <input placeholder="City, e.g. Dallas" value={city} onChange={(e) => setCity(e.target.value)} />
        <input placeholder="State, e.g. TX" value={stateRegion} onChange={(e) => setStateRegion(e.target.value)} />
        <input placeholder="Specialty, e.g. PRIMARY_CARE" value={specialty} onChange={(e) => setSpecialty(e.target.value)} />
        <button className="primary" onClick={search}>Search</button>
      </div>
      <Notice message={message} kind="error" />
      <div className="results">
        <section><h2>Healthcare facilities</h2>{facilities.length ? facilities.map((item) => <article className="result-card" key={item.facility_id}><b>{item.facility_name}</b><span>{item.facility_type}</span><p>{item.address_line_1}<br />{item.city}, {item.state_code} {item.postal_code}</p></article>) : <p className="empty">No matching facilities yet.</p>}</section>
        <section><h2>Available doctors</h2>{providers.length ? providers.map((item) => <article className="result-card" key={item.provider_id}><b>Dr. {item.first_name} {item.last_name}</b><span>{item.specialty_code.replaceAll("_", " ")}</span><p>{item.is_accepting_patients ? "Accepting new patients" : "Not accepting patients"}</p></article>) : <p className="empty">No matching doctors yet.</p>}</section>
      </div>
    </main>
  );
}

const REQUIRED_PROFILE_FIELDS = new Set([
  "first_name", "last_name", "date_of_birth", "country", "preferred_language",
]);

function pickEditable(data) {
  const out = {};
  for (const key of EDITABLE_PROFILE_FIELDS) out[key] = data[key] ?? "";
  return out;
}

function Dashboard({ accessToken }) {
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    api.profile(accessToken)
      .then((data) => { setProfile(data); setForm(pickEditable(data)); })
      .catch((error) => setMessage(error.message));
  }, [accessToken]);
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });
  const changed = form
    ? EDITABLE_PROFILE_FIELDS.filter((field) => (form[field] ?? "") !== (profile[field] ?? ""))
    : [];
  const dirty = changed.length > 0;
  const save = async () => {
    setBusy(true); setMessage("");
    try {
      const patch = Object.fromEntries(
        changed
          .filter((field) => !(REQUIRED_PROFILE_FIELDS.has(field) && !form[field]))
          .map((field) => [field, form[field] === "" ? null : form[field]]),
      );
      const data = await api.updateProfile(accessToken, patch);
      setProfile(data); setForm(pickEditable(data)); setMessage("Profile updated.");
    } catch (error) { setMessage(error.message); }
    finally { setBusy(false); }
  };
  if (!profile || !form) return <main className="directory"><Notice message={message || "Loading your profile…"} /></main>;
  const languageOptions = LANGUAGE_OPTIONS.includes(form.preferred_language) || !form.preferred_language
    ? LANGUAGE_OPTIONS
    : [form.preferred_language, ...LANGUAGE_OPTIONS];
  return (
    <main className="dashboard">
      <section className="welcome"><span className="eyebrow">Patient dashboard</span><h1>Good to see you, {profile.first_name}.</h1><p>Keep your details current so we can match you to nearby care. Correct anything that was entered incorrectly at sign up.</p></section>
      <Notice message={message} kind={message === "Profile updated." ? "success" : "error"} />
      <div className="dashboard-grid">
        <section className="panel profile-card">
          <h2>My profile</h2>
          <dl>
            <div><dt>Patient ID</dt><dd>{profile.external_patient_id}</dd></div>
            <div><dt>Email</dt><dd>{profile.email}</dd></div>
          </dl>
          <div className="form-grid">
            <label>First name<input name="first_name" value={form.first_name} onChange={update} required /></label>
            <label>Last name<input name="last_name" value={form.last_name} onChange={update} required /></label>
            <label>Date of birth<input name="date_of_birth" type="date" value={form.date_of_birth} onChange={update} required /></label>
            <label>Sex at birth<select name="sex_at_birth" value={form.sex_at_birth} onChange={update}><option value="">Prefer not to answer</option><option>FEMALE</option><option>MALE</option><option>INTERSEX</option></select></label>
            <label>Phone<input name="phone" value={form.phone} onChange={update} /></label>
            <label>Preferred language<select name="preferred_language" value={form.preferred_language} onChange={update}>{languageOptions.map((name) => <option key={name} value={name}>{name}</option>)}</select></label>
            <label>Country<input name="country" value={form.country} onChange={update} required /></label>
            <label>State / Region<input name="state" value={form.state} onChange={update} /></label>
            <label>City<input name="city" value={form.city} onChange={update} /></label>
            <label>ZIP / Postal code<input name="postal_code" value={form.postal_code} onChange={update} /></label>
          </div>
          {dirty
            ? <button className="primary full" disabled={busy} onClick={save}>{busy ? "Saving…" : "Save profile"}</button>
            : <small className="disclaimer">Your profile is up to date.</small>}
        </section>
        <section className="panel next-card"><h2>What comes next</h2><div className="timeline-item"><span>03</span><p><b>Clinical ingestion</b><br />FHIR and operational data pipelines</p></div><div className="timeline-item"><span>04</span><p><b>Oracle engineering</b><br />PL/SQL validation and recovery</p></div><div className="timeline-item"><span>06</span><p><b>Care guidance</b><br />Safe symptom-based routing</p></div></section>
      </div>
    </main>
  );
}

function Welcome({ accessToken, go }) {
  const [profile, setProfile] = useState(null);
  const [service, setService] = useState("");
  const [concern, setConcern] = useState("");
  useEffect(() => { api.profile(accessToken).then(setProfile).catch(() => {}); }, [accessToken]);
  const chosen = SERVICES.find((item) => item.id === service);
  const blocked = !service || (service === "concern" && !concern);
  const near = { city: profile?.city || "", state: profile?.state || "" };
  const start = () => {
    if (service === "directory") go("directory", near);
    else if (service === "profile") go("dashboard", {});
    else if (service === "concern") go("directory", { ...near, specialty: concern });
  };
  return (
    <main className="dashboard">
      <section className="welcome">
        <span className="eyebrow">Patient home</span>
        <h1>Welcome{profile ? `, ${profile.first_name}` : ""}.</h1>
        <p>Choose what you would like to do today.</p>
      </section>
      <div className="dashboard-grid">
        <section className="panel">
          <h2>How can we help?</h2>
          <label>Choose a service
            <select value={service} onChange={(event) => { setService(event.target.value); setConcern(""); }}>
              <option value="">Select an option…</option>
              {SERVICES.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
            </select>
          </label>
          {chosen && <p className="empty">{chosen.blurb}</p>}
          {service === "concern" && (
            <label>What kind of issue is it?
              <select value={concern} onChange={(event) => setConcern(event.target.value)}>
                <option value="">Select a concern…</option>
                {CONCERN_TO_SPECIALTY.map((item) => <option key={item.specialty} value={item.specialty}>{item.label}</option>)}
              </select>
            </label>
          )}
          <button className="primary full" disabled={blocked} onClick={start}>Continue</button>
          <small className="disclaimer">General navigation only, not medical advice. In an emergency, call your local emergency number.</small>
        </section>
        <section className="panel">
          <h2>ZambeCare services</h2>
          {SERVICES.map((item) => (
            <div className="timeline-item" key={item.id}><span>›</span><p><b>{item.label}</b><br />{item.blurb}</p></div>
          ))}
        </section>
      </div>
    </main>
  );
}

export default function App() {
  const [view, setView] = useState("home");
  const [nav, setNav] = useState({});
  const [tokens, setTokens] = useState(() => {
    const saved = sessionStorage.getItem("zambecare-session");
    return saved ? JSON.parse(saved) : null;
  });
  const go = (nextView, params = {}) => { setNav(params); setView(nextView); };
  const onLogin = (nextTokens) => { sessionStorage.setItem("zambecare-session", JSON.stringify(nextTokens)); setTokens(nextTokens); go("welcome"); };
  const logout = async () => { if (tokens) await api.logout(tokens.refresh_token).catch(() => {}); sessionStorage.removeItem("zambecare-session"); setTokens(null); go("home"); };
  return (
    <div className="site-shell">
      <header><button className="brand" onClick={() => go("home")}><span>Z</span>ZambeCare</button><nav><button onClick={() => go("directory")}>Find care</button>{tokens ? <><button onClick={() => go("welcome")}>Home</button><button onClick={() => go("dashboard")}>Dashboard</button><button className="nav-cta" onClick={logout}>Sign out</button></> : <><button onClick={() => go("login")}>Sign in</button><button className="nav-cta" onClick={() => go("register")}>Join ZambeCare</button></>}</nav></header>
      {view === "home" && <Landing setView={setView} />}
      {view === "register" && <Register setView={setView} />}
      {view === "login" && <Login onLogin={onLogin} />}
      {view === "welcome" && tokens && <Welcome accessToken={tokens.access_token} go={go} />}
      {view === "directory" && <Directory initialCity={nav.city || ""} initialState={nav.state || ""} initialSpecialty={nav.specialty || ""} />}
      {view === "dashboard" && tokens && <Dashboard accessToken={tokens.access_token} />}
      <footer><b>ZambeCare</b><span>Synthetic-data healthcare engineering portfolio</span><span>Phase 2 · 2026</span></footer>
    </div>
  );
}

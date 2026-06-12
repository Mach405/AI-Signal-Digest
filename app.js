/* ============================================================
   MowerFinder — listing app
   ------------------------------------------------------------
   LIVE DATA HOOK:
   Set DATA_SOURCE_URL to a backend endpoint that returns an
   array of listings in the shape below, and the grid will use
   live results instead of the bundled SAMPLE_LISTINGS.

   Listing shape:
   {
     id, brand, model, year, hours, price, hp,
     discharge: "rear" | "side",
     location, image, url, rating, dealer
   }
   ============================================================ */

const DATA_SOURCE_URL = null; // e.g. "https://your-api.example.com/mowers"

/* ---- Sample listings (John Deere + Kubota zero-turns) ---- */
const SAMPLE_LISTINGS = [
  { id: 1,  brand: "John Deere", model: "Z930M",  year: 2022, hours: 220,  price: 11900, hp: 25, discharge: "rear", location: "Springfield, MO",  rating: 4.9, dealer: "MachineFinder", image: img("#367c2b","JD Z930M") },
  { id: 2,  brand: "John Deere", model: "Z720E",  year: 2020, hours: 540,  price: 7400,  hp: 23, discharge: "side", location: "Dallas, TX",      rating: 4.7, dealer: "TractorHouse", image: img("#367c2b","JD Z720E") },
  { id: 3,  brand: "Kubota",     model: "Z421",   year: 2021, hours: 310,  price: 8900,  hp: 22, discharge: "side", location: "Lincoln, NE",     rating: 4.8, dealer: "Kubota Dealer", image: img("#fa4616","Kubota Z421") },
  { id: 4,  brand: "Kubota",     model: "Z781i",  year: 2023, hours: 95,   price: 14200, hp: 31, discharge: "rear", location: "Boise, ID",       rating: 5.0, dealer: "Kubota Dealer", image: img("#fa4616","Kubota Z781i") },
  { id: 5,  brand: "John Deere", model: "Z915E",  year: 2019, hours: 880,  price: 6200,  hp: 22, discharge: "side", location: "Columbus, OH",    rating: 4.5, dealer: "Machinery Pete", image: img("#367c2b","JD Z915E") },
  { id: 6,  brand: "John Deere", model: "Z994R",  year: 2023, hours: 60,   price: 16800, hp: 38, discharge: "rear", location: "Fresno, CA",      rating: 4.9, dealer: "MachineFinder", image: img("#367c2b","JD Z994R") },
  { id: 7,  brand: "Kubota",     model: "Z125S",  year: 2018, hours: 1240, price: 4300,  hp: 24, discharge: "side", location: "Tulsa, OK",       rating: 4.3, dealer: "Craigslist",   image: img("#fa4616","Kubota Z125S") },
  { id: 8,  brand: "Kubota",     model: "ZD1211", year: 2022, hours: 410,  price: 13500, hp: 24, discharge: "rear", location: "Madison, WI",     rating: 4.8, dealer: "Kubota Dealer", image: img("#fa4616","Kubota ZD1211") },
  { id: 9,  brand: "John Deere", model: "Z530M",  year: 2021, hours: 340,  price: 6900,  hp: 24, discharge: "side", location: "Raleigh, NC",     rating: 4.6, dealer: "TractorHouse", image: img("#367c2b","JD Z530M") },
  { id: 10, brand: "Kubota",     model: "Z724X",  year: 2020, hours: 600,  price: 9100,  hp: 24, discharge: "side", location: "Salt Lake City, UT", rating: 4.7, dealer: "Machinery Pete", image: img("#fa4616","Kubota Z724X") },
  { id: 11, brand: "John Deere", model: "Z950R",  year: 2024, hours: 25,   price: 18900, hp: 31, discharge: "rear", location: "Bozeman, MT",     rating: 5.0, dealer: "MachineFinder", image: img("#367c2b","JD Z950R") },
  { id: 12, brand: "Kubota",     model: "Z411",   year: 2017, hours: 1680, price: 3800,  hp: 19, discharge: "side", location: "Little Rock, AR", rating: 4.1, dealer: "Facebook Marketplace", image: img("#fa4616","Kubota Z411") },
  { id: 13, brand: "John Deere", model: "Z740R",  year: 2022, hours: 180,  price: 10400, hp: 25, discharge: "rear", location: "Des Moines, IA",  rating: 4.8, dealer: "TractorHouse", image: img("#367c2b","JD Z740R") },
  { id: 14, brand: "Kubota",     model: "Z781KW", year: 2023, hours: 140,  price: 13900, hp: 31, discharge: "rear", location: "Spokane, WA",     rating: 4.9, dealer: "Kubota Dealer", image: img("#fa4616","Kubota Z781KW") },
  { id: 15, brand: "John Deere", model: "Z355E",  year: 2019, hours: 720,  price: 3200,  hp: 22, discharge: "side", location: "Knoxville, TN",   rating: 4.2, dealer: "Craigslist",   image: img("#367c2b","JD Z355E") },
  { id: 16, brand: "Kubota",     model: "ZD1511", year: 2024, hours: 40,   price: 21500, hp: 31, discharge: "rear", location: "Sacramento, CA",  rating: 5.0, dealer: "Kubota Dealer", image: img("#fa4616","Kubota ZD1511") },
  { id: 17, brand: "John Deere", model: "Z920M",  year: 2021, hours: 460,  price: 9600,  hp: 23, discharge: "side", location: "Wichita, KS",     rating: 4.6, dealer: "Machinery Pete", image: img("#367c2b","JD Z920M") },
  { id: 18, brand: "Kubota",     model: "Z421KW", year: 2022, hours: 270,  price: 9800,  hp: 24, discharge: "side", location: "Eugene, OR",      rating: 4.7, dealer: "TractorHouse", image: img("#fa4616","Kubota Z421KW") },
  { id: 19, brand: "John Deere", model: "Z960M",  year: 2023, hours: 110,  price: 15400, hp: 35, discharge: "rear", location: "Lubbock, TX",     rating: 4.9, dealer: "MachineFinder", image: img("#367c2b","JD Z960M") },
  { id: 20, brand: "Kubota",     model: "Z251",   year: 2018, hours: 990,  price: 5100,  hp: 21, discharge: "side", location: "Billings, MT",    rating: 4.3, dealer: "Facebook Marketplace", image: img("#fa4616","Kubota Z251") },
];

/* Inline SVG placeholder image so the page works fully offline */
function img(color, label) {
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600'>
    <rect width='600' height='600' fill='${color}'/>
    <rect y='430' width='600' height='170' fill='rgba(0,0,0,0.18)'/>
    <text x='50%' y='280' font-family='Inter,sans-serif' font-size='46' font-weight='800' fill='white' text-anchor='middle'>${label}</text>
    <text x='50%' y='520' font-family='Inter,sans-serif' font-size='30' fill='rgba(255,255,255,0.9)' text-anchor='middle'>Zero-Turn Mower</text>
  </svg>`;
  return "data:image/svg+xml," + encodeURIComponent(svg);
}

/* ---- State ---- */
let LISTINGS = SAMPLE_LISTINGS;
const favorites = new Set();
const state = {
  brand: "all",
  model: "",
  year: "",
  discharge: "",
  maxPrice: 25000,
  maxHours: 2500,
  minHp: 0,
  keyword: "",
  sort: "newest",
};

/* ---- Elements ---- */
const $ = (id) => document.getElementById(id);
const grid = $("grid");
const empty = $("empty");

/* ---- Init ---- */
async function init() {
  if (DATA_SOURCE_URL) {
    try {
      const res = await fetch(DATA_SOURCE_URL);
      const data = await res.json();
      if (Array.isArray(data) && data.length) LISTINGS = data;
    } catch (e) {
      console.warn("Live data fetch failed, falling back to samples:", e);
    }
  }
  populateModelOptions();
  populateYearOptions();
  wireEvents();
  render();
}

function populateModelOptions() {
  const sel = $("fModel");
  const models = [...new Set(LISTINGS.map((l) => l.model))].sort();
  models.forEach((m) => sel.append(new Option(m, m)));
}

function populateYearOptions() {
  const sel = $("fYear");
  const years = [...new Set(LISTINGS.map((l) => l.year))].sort((a, b) => b - a);
  years.forEach((y) => sel.append(new Option(y, y)));
}

/* ---- Events ---- */
function wireEvents() {
  document.querySelectorAll("#brandChips .chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll("#brandChips .chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      state.brand = chip.dataset.brand;
      render();
    });
  });

  $("fModel").addEventListener("change", (e) => { state.model = e.target.value; render(); });
  $("fYear").addEventListener("change", (e) => { state.year = e.target.value; render(); });
  $("fDischarge").addEventListener("change", (e) => { state.discharge = e.target.value; render(); });
  $("sortBy").addEventListener("change", (e) => { state.sort = e.target.value; render(); });

  $("fPrice").addEventListener("input", (e) => {
    state.maxPrice = +e.target.value;
    $("priceVal").textContent = "$" + state.maxPrice.toLocaleString();
    render();
  });
  $("fHours").addEventListener("input", (e) => {
    state.maxHours = +e.target.value;
    $("hoursVal").textContent = state.maxHours.toLocaleString();
    render();
  });
  $("fHp").addEventListener("input", (e) => {
    state.minHp = +e.target.value;
    $("hpVal").textContent = state.minHp + " hp";
    render();
  });

  $("keyword").addEventListener("input", (e) => { state.keyword = e.target.value.toLowerCase(); render(); });
  $("searchBtn").addEventListener("click", render);

  $("resetBtn").addEventListener("click", resetFilters);

  $("sourcesBtn").addEventListener("click", () => ($("sourcesModal").hidden = false));
  $("sourcesClose").addEventListener("click", () => ($("sourcesModal").hidden = true));
  $("sourcesModal").addEventListener("click", (e) => {
    if (e.target.id === "sourcesModal") e.target.hidden = true;
  });
}

function resetFilters() {
  Object.assign(state, { brand: "all", model: "", year: "", discharge: "", maxPrice: 25000, maxHours: 2500, minHp: 0, keyword: "", sort: "newest" });
  $("fModel").value = ""; $("fYear").value = ""; $("fDischarge").value = "";
  $("fPrice").value = 25000; $("fHours").value = 2500; $("fHp").value = 0;
  $("keyword").value = ""; $("sortBy").value = "newest";
  $("priceVal").textContent = "$25,000"; $("hoursVal").textContent = "2,500"; $("hpVal").textContent = "0 hp";
  document.querySelectorAll("#brandChips .chip").forEach((c) => c.classList.toggle("active", c.dataset.brand === "all"));
  render();
}

/* ---- Filtering + sorting ---- */
function applyFilters() {
  let out = LISTINGS.filter((l) => {
    if (state.brand !== "all" && l.brand !== state.brand) return false;
    if (state.model && l.model !== state.model) return false;
    if (state.year && l.year < +state.year) return false;
    if (state.discharge && l.discharge !== state.discharge) return false;
    if (l.price > state.maxPrice) return false;
    if (l.hours > state.maxHours) return false;
    if (l.hp < state.minHp) return false;
    if (state.keyword) {
      const hay = `${l.brand} ${l.model} ${l.location} ${l.dealer}`.toLowerCase();
      if (!hay.includes(state.keyword)) return false;
    }
    return true;
  });

  const sorters = {
    newest: (a, b) => b.year - a.year || a.hours - b.hours,
    priceAsc: (a, b) => a.price - b.price,
    priceDesc: (a, b) => b.price - a.price,
    hoursAsc: (a, b) => a.hours - b.hours,
    yearDesc: (a, b) => b.year - a.year,
  };
  return out.sort(sorters[state.sort] || sorters.newest);
}

/* ---- Render ---- */
function render() {
  const items = applyFilters();
  $("resultCount").textContent = `${items.length} mower${items.length === 1 ? "" : "s"} found`;
  empty.hidden = items.length > 0;
  grid.innerHTML = items.map(cardHTML).join("");

  grid.querySelectorAll(".fav").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = +btn.dataset.id;
      if (favorites.has(id)) favorites.delete(id); else favorites.add(id);
      btn.classList.toggle("on", favorites.has(id));
      btn.textContent = favorites.has(id) ? "♥" : "♡";
    });
  });

  grid.querySelectorAll(".card").forEach((card) => {
    card.addEventListener("click", () => {
      const url = card.dataset.url;
      if (url && url !== "#") window.open(url, "_blank");
    });
  });
}

function cardHTML(l) {
  const dischargeLabel = l.discharge === "rear" ? "Rear discharge" : "Side discharge";
  const fav = favorites.has(l.id);
  return `
    <article class="card" data-url="${l.url || "#"}">
      <div class="card-media">
        <img src="${l.image}" alt="${l.brand} ${l.model}" loading="lazy" />
        <span class="card-badge">${l.brand}</span>
        <button class="fav ${fav ? "on" : ""}" data-id="${l.id}" aria-label="Save">${fav ? "♥" : "♡"}</button>
      </div>
      <div class="card-body">
        <div class="card-row">
          <h3 class="card-title">${l.brand} ${l.model}</h3>
          <span class="rating">${l.rating.toFixed(1)}</span>
        </div>
        <p class="card-loc">${l.location} · ${l.dealer}</p>
        <div class="card-specs">
          <span class="spec">${l.year}</span>
          <span class="spec">${l.hours.toLocaleString()} hrs</span>
          <span class="spec">${l.hp} hp</span>
          <span class="spec">${dischargeLabel}</span>
        </div>
        <p class="card-price">$${l.price.toLocaleString()} <span>· used</span></p>
      </div>
    </article>`;
}

init();

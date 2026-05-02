// Country picker. Production version reads the country list from BigQuery via the API.

const SAMPLE = [
  { iso3: "COG", name: "Republic of Congo" },
  { iso3: "NGA", name: "Nigeria" },
  { iso3: "KEN", name: "Kenya" },
  { iso3: "ZAF", name: "South Africa" },
  { iso3: "MAR", name: "Morocco" },
  { iso3: "EGY", name: "Egypt" },
];

export default function CountriesPage() {
  return (
    <main className="min-h-screen p-12">
      <h1 className="text-3xl font-semibold mb-6">Countries</h1>
      <ul className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {SAMPLE.map((c) => (
          <li key={c.iso3}>
            <a
              href={`/countries/${c.iso3}`}
              className="block rounded-xl border border-white/10 p-4 hover:border-[var(--accent)]"
            >
              <span className="text-sm text-[var(--muted)]">{c.iso3}</span>
              <div className="text-lg">{c.name}</div>
            </a>
          </li>
        ))}
      </ul>
    </main>
  );
}

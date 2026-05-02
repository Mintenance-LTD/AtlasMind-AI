// Country profile — pulls scores + claims for the country from the API.

type Props = { params: Promise<{ iso3: string }> };

const SCORES = [
  "political_risk",
  "market_opportunity",
  "investment_readiness",
  "demographic_growth",
  "technology_adoption",
  "infrastructure_gap",
  "strategic_importance",
];

export default async function CountryProfile({ params }: Props) {
  const { iso3 } = await params;

  return (
    <main className="min-h-screen p-12">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold">{iso3.toUpperCase()}</h1>
        <p className="text-[var(--muted)] mt-1">Country profile</p>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
        {SCORES.map((s) => (
          <div key={s} className="rounded-xl border border-white/10 p-4">
            <div className="text-xs text-[var(--muted)] uppercase tracking-wide">
              {s.replace(/_/g, " ")}
            </div>
            <div className="text-3xl font-light mt-2">—</div>
          </div>
        ))}
      </section>

      <form action="/api/runs" method="post" className="flex gap-3 items-center">
        <input type="hidden" name="country" value={iso3} />
        <label className="text-[var(--muted)] text-sm">Horizon</label>
        <select name="horizon_months" className="bg-transparent border border-white/10 rounded px-3 py-1">
          <option value="12">12 months</option>
          <option value="24" selected>
            24 months
          </option>
          <option value="60">60 months</option>
        </select>
        <button
          type="submit"
          className="bg-[var(--accent)] text-white rounded px-4 py-2 text-sm"
        >
          Generate briefing
        </button>
      </form>
    </main>
  );
}

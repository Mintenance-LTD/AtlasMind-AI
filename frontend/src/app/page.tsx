export default function Home() {
  return (
    <main className="min-h-screen p-12">
      <header className="mb-12">
        <h1 className="text-4xl font-semibold">AtlasMind AI</h1>
        <p className="text-[var(--muted)] mt-2">
          Strategic Intelligence Operating System.
        </p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <a
          href="/countries"
          className="rounded-2xl border border-white/10 p-6 hover:border-[var(--accent)] transition"
        >
          <h2 className="text-xl font-medium">Countries</h2>
          <p className="text-[var(--muted)] mt-1">
            Browse country profiles, scores, and run a new briefing.
          </p>
        </a>
        <a
          href="/runs"
          className="rounded-2xl border border-white/10 p-6 hover:border-[var(--accent)] transition"
        >
          <h2 className="text-xl font-medium">Briefings</h2>
          <p className="text-[var(--muted)] mt-1">
            See your past runs and the Doc / Slides / Sheet outputs in Drive.
          </p>
        </a>
      </section>
    </main>
  );
}

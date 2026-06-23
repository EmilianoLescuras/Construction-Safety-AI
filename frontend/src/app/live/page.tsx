"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect, useState } from "react";

import { RuleBadge } from "@/components/event-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";

const POLL_MS = 3000;

export default function LivePage() {
  const [paused, setPaused] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const { data, isLoading, error, isFetching } = useQuery({
    queryKey: ["live-events"],
    queryFn: () => api.listEvents({ limit: 20 }),
    refetchInterval: paused ? false : POLL_MS,
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (data) setLastUpdated(new Date());
  }, [data]);

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="flex items-center gap-3 text-2xl font-semibold tracking-tight">
            Live monitor
            {!paused && (
              <span className="inline-flex h-2.5 w-2.5 animate-pulse rounded-full bg-red-500" />
            )}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Polling /events every {POLL_MS / 1000}s. Last 20 violations.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          {lastUpdated && (
            <span>updated {lastUpdated.toLocaleTimeString()}</span>
          )}
          {isFetching && !paused && <span>refreshing…</span>}
          <button
            type="button"
            onClick={() => setPaused((p) => !p)}
            className="rounded-md border px-3 py-1.5 text-sm"
          >
            {paused ? "Resume" : "Pause"}
          </button>
        </div>
      </div>

      {error ? (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-4 text-sm">
          {error.message}
        </div>
      ) : null}

      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44" />
          ))}
        </div>
      ) : !data || data.length === 0 ? (
        <div className="rounded-md border bg-muted/40 p-10 text-center text-sm text-muted-foreground">
          No events yet. Run the alerts pipeline and they will appear here.
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((ev) => {
            const crop = ev.evidence_files.find((e) => e.kind === "crop");
            return (
              <Link key={ev.id} href={`/events/${ev.id}`} className="block">
                <Card className="transition hover:border-foreground/30">
                  <CardHeader className="flex-row items-center justify-between gap-2">
                    <CardTitle className="text-sm">
                      Worker #{ev.person_id}
                    </CardTitle>
                    <RuleBadge rule={ev.rule} />
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {crop ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={api.evidenceUrl(crop.id)}
                        alt={`Crop for event ${ev.id}`}
                        className="h-28 w-full rounded-md border object-cover"
                      />
                    ) : (
                      <div className="flex h-28 items-center justify-center rounded-md border bg-muted/30 text-xs text-muted-foreground">
                        no crop
                      </div>
                    )}
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span className="font-mono">
                        conf {ev.violation_conf.toFixed(2)} ·{" "}
                        {ev.duration_seconds.toFixed(1)}s
                      </span>
                      <span>{new Date(ev.ingested_at).toLocaleTimeString()}</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

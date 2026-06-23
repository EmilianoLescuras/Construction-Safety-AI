"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { use } from "react";

import { RuleBadge, SinkBadge } from "@/components/event-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";

export default function EventDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const eventId = Number(id);

  const { data, isLoading, error } = useQuery({
    queryKey: ["event", eventId],
    queryFn: () => api.getEvent(eventId),
  });

  if (isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  if (error || !data) {
    return (
      <div className="rounded-md border border-destructive/40 bg-destructive/10 p-4 text-sm">
        Could not load event #{eventId}: {error?.message ?? "not found"}
      </div>
    );
  }

  const full = data.evidence_files.find((e) => e.kind === "full");
  const crop = data.evidence_files.find((e) => e.kind === "crop");

  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/events"
          className="text-sm text-muted-foreground hover:underline"
        >
          ← Events
        </Link>
        <div className="mt-2 flex items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight">
            Event #{data.id}
          </h1>
          <RuleBadge rule={data.rule} />
        </div>
        <p className="mt-1 font-mono text-sm text-muted-foreground">
          worker #{data.person_id} · frame {data.frame} · conf{" "}
          {data.violation_conf.toFixed(2)} · {data.duration_seconds.toFixed(1)}s
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Annotated frame</CardTitle>
          </CardHeader>
          <CardContent>
            {full ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={api.evidenceUrl(full.id)}
                alt={`Full frame for event ${data.id}`}
                className="w-full rounded-md border"
              />
            ) : (
              <div className="py-12 text-center text-sm text-muted-foreground">
                No full-frame evidence stored.
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Worker crop</CardTitle>
          </CardHeader>
          <CardContent>
            {crop ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={api.evidenceUrl(crop.id)}
                alt={`Crop for event ${data.id}`}
                className="max-h-96 rounded-md border"
              />
            ) : (
              <div className="py-12 text-center text-sm text-muted-foreground">
                No crop stored.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Metadata</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm md:grid-cols-3">
            <Field k="Violation class" v={data.violation_class} />
            <Field k="Source" v={data.source ?? "—"} mono />
            <Field k="Ingested" v={new Date(data.ingested_at).toLocaleString()} />
            <Field k="First seen ts" v={`${data.first_seen_ts.toFixed(2)}s`} mono />
            <Field k="Emitted ts" v={`${data.emitted_ts.toFixed(2)}s`} mono />
            <Field
              k="Person bbox"
              v={data.person_bbox.map((n) => n.toFixed(0)).join(", ")}
              mono
            />
            <Field
              k="Violation bbox"
              v={data.violation_bbox.map((n) => n.toFixed(0)).join(", ")}
              mono
            />
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Dispatches</CardTitle>
        </CardHeader>
        <CardContent>
          {data.dispatches.length === 0 ? (
            <div className="py-6 text-center text-sm text-muted-foreground">
              No dispatch recorded.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Sink</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Dispatched</TableHead>
                  <TableHead>Error</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.dispatches.map((d) => (
                  <TableRow key={d.id}>
                    <TableCell>
                      <SinkBadge sink={d.sink} success={d.success} />
                    </TableCell>
                    <TableCell className="text-sm">
                      {d.success ? "Success" : "Failed"}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      {new Date(d.dispatched_at * 1000).toLocaleString()}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-destructive">
                      {d.error}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Separator />
    </div>
  );
}

function Field({ k, v, mono }: { k: string; v: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{k}</dt>
      <dd className={mono ? "font-mono" : ""}>{v}</dd>
    </div>
  );
}

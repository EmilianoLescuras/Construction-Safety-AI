"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api } from "@/lib/api";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function KpiCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-semibold tracking-tight">{value}</div>
        {hint && (
          <div className="mt-1 text-xs text-muted-foreground">{hint}</div>
        )}
      </CardContent>
    </Card>
  );
}

export default function Page() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["stats"],
    queryFn: api.stats,
  });

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-md border border-destructive/40 bg-destructive/10 p-4 text-sm">
        Failed to load stats: {error?.message ?? "unknown error"}.
        <div className="mt-1 text-xs text-muted-foreground">
          Is the FastAPI backend running on{" "}
          {process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"}?
        </div>
      </div>
    );
  }

  const successRate =
    data.total_dispatches > 0
      ? Math.round((data.dispatch_success / data.total_dispatches) * 100)
      : 0;

  return (
    <div className="space-y-8">
      <Card className="overflow-hidden border-red-500/30 bg-gradient-to-br from-red-500/10 via-background to-amber-500/5">
        <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <div className="text-xs font-semibold uppercase tracking-wider text-red-600">
              New
            </div>
            <h2 className="text-xl font-semibold tracking-tight">
              Watch the model catch unsafe workers — live demo with video + 24
              test images
            </h2>
            <p className="text-sm text-muted-foreground">
              See annotated predictions, toggle boxes on/off, and filter by
              violation vs compliant.
            </p>
          </div>
          <Link href="/demo" className={buttonVariants({ size: "lg" })}>
            Open the demo →
          </Link>
        </CardContent>
      </Card>

      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Aggregate PPE violations + alert dispatch health across all sources.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Total events" value={data.total_events} />
        <KpiCard label="Total dispatches" value={data.total_dispatches} />
        <KpiCard
          label="Dispatch success"
          value={`${successRate}%`}
          hint={`${data.dispatch_success} ok / ${data.dispatch_failed} failed`}
        />
        <KpiCard label="Rules triggered" value={data.by_rule.length} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Violations by rule</CardTitle>
          </CardHeader>
          <CardContent>
            {data.by_rule.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No events yet.
              </div>
            ) : (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.by_rule}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      className="stroke-muted"
                    />
                    <XAxis dataKey="rule" className="text-xs" />
                    <YAxis allowDecimals={false} className="text-xs" />
                    <Tooltip
                      contentStyle={{
                        background: "var(--background)",
                        border: "1px solid var(--border)",
                        borderRadius: "0.5rem",
                        fontSize: "0.75rem",
                      }}
                    />
                    <Bar dataKey="count" fill="#dc2626" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top offenders</CardTitle>
          </CardHeader>
          <CardContent>
            {data.top_persons.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No events yet.
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Worker ID</TableHead>
                    <TableHead className="text-right">Violations</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.top_persons.map((p) => (
                    <TableRow key={p.person_id}>
                      <TableCell className="font-mono">
                        #{p.person_id}
                      </TableCell>
                      <TableCell className="text-right">{p.count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

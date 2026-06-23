"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type Item = {
  id: string;
  original: string;
  prediction: string;
  width: number;
  height: number;
  status: "VIOLATION" | "COMPLIANT" | "NO-DETECTION";
  persons: number;
  violations: number;
  compliances: number;
  detected: Record<string, number>;
  source_name: string;
};

type Manifest = { items: Item[] };

const VIOLATION_CLASSES = new Set(["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]);
const COMPLIANCE_CLASSES = new Set([
  "Hardhat",
  "Mask",
  "Safety Vest",
  "Gloves",
]);

function classChipColor(name: string) {
  if (VIOLATION_CLASSES.has(name))
    return "bg-red-500/15 text-red-700 dark:text-red-300 border-red-500/40";
  if (COMPLIANCE_CLASSES.has(name))
    return "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/40";
  if (name === "Person")
    return "bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/40";
  return "bg-muted text-muted-foreground";
}

function StatusBadge({ status }: { status: Item["status"] }) {
  if (status === "VIOLATION") {
    return (
      <Badge className="bg-red-600 text-white hover:bg-red-600">
        ✕ VIOLATION
      </Badge>
    );
  }
  if (status === "COMPLIANT") {
    return (
      <Badge className="bg-emerald-600 text-white hover:bg-emerald-600">
        ✓ COMPLIANT
      </Badge>
    );
  }
  return <Badge variant="outline">no detection</Badge>;
}

function ImageCompare({ item }: { item: Item }) {
  const [showPred, setShowPred] = useState(true);
  return (
    <Card className="overflow-hidden">
      <div className="relative aspect-video bg-muted">
        <Image
          src={"/demo/" + (showPred ? item.prediction : item.original)}
          alt={item.source_name}
          fill
          sizes="(max-width: 1024px) 100vw, 50vw"
          className="object-contain"
        />
        <div className="absolute left-3 top-3">
          <StatusBadge status={item.status} />
        </div>
        <button
          type="button"
          onClick={() => setShowPred((v) => !v)}
          className="absolute right-3 top-3 rounded-md bg-black/60 px-2 py-1 text-xs text-white backdrop-blur hover:bg-black/80"
        >
          {showPred ? "Hide boxes" : "Show boxes"}
        </button>
      </div>
      <CardContent className="space-y-3 pt-4">
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(item.detected).length === 0 && (
            <span className="text-xs text-muted-foreground">
              No detections above threshold
            </span>
          )}
          {Object.entries(item.detected)
            .sort((a, b) => b[1] - a[1])
            .map(([name, n]) => (
              <span
                key={name}
                className={
                  "inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11px] " +
                  classChipColor(name)
                }
              >
                {name}
                {n > 1 && <span className="opacity-70">×{n}</span>}
              </span>
            ))}
        </div>
        <div className="grid grid-cols-3 gap-3 text-center text-xs">
          <div>
            <div className="text-lg font-semibold">{item.persons}</div>
            <div className="text-muted-foreground">people</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-red-600">
              {item.violations}
            </div>
            <div className="text-muted-foreground">violations</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-emerald-600">
              {item.compliances}
            </div>
            <div className="text-muted-foreground">compliant PPE</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

const RULES = [
  {
    code: "vest",
    title: "Safety Vest",
    description:
      "If a tracked person stays without a high-visibility vest for ≥3s, fires a violation. 30s cooldown per worker.",
    color: "bg-red-500",
  },
  {
    code: "helmet",
    title: "Hardhat",
    description:
      "Person detected without a hardhat for ≥3s. Critical on active construction sites.",
    color: "bg-amber-500",
  },
  {
    code: "mask",
    title: "Mask",
    description:
      "Person without a mask for ≥3s — relevant in dust-heavy or sanitary zones.",
    color: "bg-sky-500",
  },
] as const;

export default function DemoPage() {
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [filter, setFilter] = useState<"all" | "VIOLATION" | "COMPLIANT">(
    "all",
  );

  useEffect(() => {
    fetch("/demo/manifest.json")
      .then((r) => r.json())
      .then(setManifest)
      .catch(() => setManifest({ items: [] }));
  }, []);

  const items = useMemo(() => manifest?.items ?? [], [manifest]);
  const visible = useMemo(
    () => (filter === "all" ? items : items.filter((i) => i.status === filter)),
    [items, filter],
  );

  const counts = useMemo(() => {
    return {
      total: items.length,
      violations: items.filter((i) => i.status === "VIOLATION").length,
      compliant: items.filter((i) => i.status === "COMPLIANT").length,
      none: items.filter((i) => i.status === "NO-DETECTION").length,
    };
  }, [items]);

  return (
    <div className="space-y-12">
      {/* HERO */}
      <section className="space-y-6">
        <div className="space-y-2">
          <Badge variant="outline" className="text-xs">
            Live demo · YOLOv8n · 19 classes
          </Badge>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            See the system catch unsafe workers — in real time
          </h1>
          <p className="max-w-3xl text-muted-foreground">
            Below is a real run of the inference pipeline on a construction
            site clip and a sample of 24 unseen test images. Red boxes are{" "}
            <strong>safety violations</strong> (missing helmet, vest, or mask).
            Green boxes are <strong>compliant PPE</strong>.
          </p>
        </div>

        <Card className="overflow-hidden">
          <div className="grid gap-0 md:grid-cols-5">
            <div className="md:col-span-3 bg-black">
              <video
                src="/demo/sample_run.mp4"
                controls
                autoPlay
                loop
                muted
                playsInline
                className="aspect-video w-full"
              />
            </div>
            <div className="space-y-4 p-6 md:col-span-2">
              <div>
                <h2 className="text-lg font-semibold">
                  What you&apos;re watching
                </h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  YOLOv8 detects PPE per frame, ByteTrack assigns persistent
                  worker IDs, and the rule engine fires an event when a worker
                  stays out of compliance for ≥3 seconds.
                </p>
              </div>
              <div className="space-y-3">
                {RULES.map((r) => (
                  <div key={r.code} className="flex items-start gap-3">
                    <span className={"mt-1 h-2.5 w-2.5 rounded-full " + r.color} />
                    <div>
                      <div className="text-sm font-medium">{r.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {r.description}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex gap-2 pt-2">
                <Link href="/events" className={buttonVariants({ size: "sm" })}>
                  View all events
                </Link>
                <Link
                  href="/live"
                  className={buttonVariants({ size: "sm", variant: "outline" })}
                >
                  Open live monitor
                </Link>
              </div>
            </div>
          </div>
        </Card>
      </section>

      {/* GALLERY */}
      <section className="space-y-4">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight">
              Test-set gallery — 24 images the model has never seen
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Toggle <em>Hide boxes</em> to compare raw input vs the model&apos;s
              prediction. Click the chips to inspect each detected class.
            </p>
          </div>
          <div className="flex gap-2">
            {(["all", "VIOLATION", "COMPLIANT"] as const).map((k) => (
              <button
                key={k}
                type="button"
                onClick={() => setFilter(k)}
                className={
                  "rounded-md border px-3 py-1.5 text-xs transition-colors " +
                  (filter === k
                    ? "border-foreground bg-foreground text-background"
                    : "hover:bg-muted")
                }
              >
                {k === "all" ? `All (${counts.total})` : null}
                {k === "VIOLATION" ? `Violations (${counts.violations})` : null}
                {k === "COMPLIANT" ? `Compliant (${counts.compliant})` : null}
              </button>
            ))}
          </div>
        </div>

        {!manifest && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="aspect-video animate-pulse rounded-md bg-muted"
              />
            ))}
          </div>
        )}

        {manifest && visible.length === 0 && (
          <div className="rounded-md border p-6 text-center text-sm text-muted-foreground">
            No items match this filter.
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visible.map((item) => (
            <ImageCompare key={item.id} item={item} />
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold tracking-tight">
          How it works under the hood
        </h2>
        <div className="grid gap-4 md:grid-cols-4">
          {[
            {
              n: "1",
              t: "Detect",
              d: "YOLOv8n predicts 19 classes per frame at ~37 fps on Apple Silicon.",
            },
            {
              n: "2",
              t: "Track",
              d: "ByteTrack assigns a persistent ID to each worker across frames.",
            },
            {
              n: "3",
              t: "Reason",
              d: "Declarative rules fire only when a worker is out of compliance for ≥3s.",
            },
            {
              n: "4",
              t: "Alert + persist",
              d: "Events go to Postgres + a pluggable dispatcher (console / Telegram / email).",
            },
          ].map((s) => (
            <Card key={s.n}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <span className="grid h-6 w-6 place-items-center rounded-full bg-foreground text-xs text-background">
                    {s.n}
                  </span>
                  {s.t}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                {s.d}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}

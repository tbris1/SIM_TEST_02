/**
 * NewsTrendTabs: Display historical vitals with NEWS2 scores in nested tabs
 * Shows trend of patient deterioration/improvement over time
 */

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Heart,
  Activity,
  Thermometer,
  Wind,
  Droplets,
  Brain,
  AlertTriangle,
  TrendingUp,
} from 'lucide-react';
import type { VitalSignsResponse } from '@/api/types';

interface NewsTrendTabsProps {
  vitalsHistory: VitalSignsResponse[];
}

/**
 * Helper: Extract time from ISO timestamp (e.g., "2026-01-28T06:00:00" → "06:00")
 */
function formatTime(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  } catch {
    return timestamp;
  }
}

/**
 * Helper: Get NEWS score color variant and label
 */
function getNewsRiskInfo(score: number): {
  variant: 'destructive' | 'default' | 'outline';
  label: string;
  recommendation: string;
  colorClass: string;
} {
  if (score >= 7) {
    return {
      variant: 'destructive',
      label: 'High Risk',
      recommendation: 'Emergency assessment by clinical team - consider ICU',
      colorClass: 'bg-destructive/10 border-destructive',
    };
  } else if (score >= 5) {
    return {
      variant: 'default',
      label: 'Medium Risk',
      recommendation: 'Urgent review by clinician skilled in acute illness',
      colorClass: 'bg-amber-500/10 border-amber-500',
    };
  } else if (score >= 1) {
    return {
      variant: 'outline',
      label: 'Low Risk',
      recommendation: 'Monitor at least every 4-6 hours',
      colorClass: 'bg-green-500/10 border-green-500',
    };
  } else {
    return {
      variant: 'outline',
      label: 'Low Risk',
      recommendation: 'Continue routine monitoring',
      colorClass: 'bg-green-500/10 border-green-500',
    };
  }
}

export function NewsTrendTabs({ vitalsHistory }: NewsTrendTabsProps) {
  // Sort vitals in reverse chronological order (most recent first)
  const sortedVitals = [...vitalsHistory].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  // Use controlled tabs to persist selection across re-renders
  const [selectedTab, setSelectedTab] = useState<string>(sortedVitals[0]?.timestamp || '');

  // Track the previous vitals count to detect when new vitals are added
  const [prevVitalsCount, setPrevVitalsCount] = useState(sortedVitals.length);

  // Update selected tab ONLY when new vitals are added (count increases)
  useEffect(() => {
    if (sortedVitals.length > prevVitalsCount && sortedVitals.length > 0) {
      // New vitals added - select the most recent one
      setSelectedTab(sortedVitals[0].timestamp);
      setPrevVitalsCount(sortedVitals.length);
    } else if (sortedVitals.length !== prevVitalsCount) {
      // Vitals count changed (e.g., new session started)
      setPrevVitalsCount(sortedVitals.length);
      if (sortedVitals.length > 0) {
        setSelectedTab(sortedVitals[0].timestamp);
      }
    }
  }, [sortedVitals.length, prevVitalsCount, sortedVitals]);

  // Handle empty state
  if (sortedVitals.length === 0) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center">
            <Activity className="h-12 w-12 mx-auto mb-3 text-muted-foreground opacity-50" />
            <p className="text-muted-foreground">No vital signs history available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Trend Header */}
      <div className="flex items-center gap-2">
        <TrendingUp className="h-5 w-5 text-muted-foreground" />
        <h3 className="text-lg font-semibold">NEWS2 Score Trend</h3>
        <Badge variant="outline" className="ml-auto">
          {sortedVitals.length} reading{sortedVitals.length !== 1 ? 's' : ''}
        </Badge>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
        <TabsList className="w-full justify-start overflow-x-auto flex-nowrap h-auto">
          {sortedVitals.map((vitals) => {
            const riskInfo = getNewsRiskInfo(vitals.news_score);
            return (
              <TabsTrigger
                key={vitals.timestamp}
                value={vitals.timestamp}
                className="gap-2 flex-shrink-0 data-[state=active]:bg-primary/10"
              >
                <span className="font-mono text-sm">
                  {formatTime(vitals.timestamp)}
                </span>
                <Badge variant={riskInfo.variant} className="text-xs">
                  NEWS {vitals.news_score}
                </Badge>
              </TabsTrigger>
            );
          })}
        </TabsList>

        {sortedVitals.map((vitals) => {
          const riskInfo = getNewsRiskInfo(vitals.news_score);

          return (
            <TabsContent
              key={vitals.timestamp}
              value={vitals.timestamp}
              className="mt-4 space-y-4"
            >
              {/* NEWS Score Banner */}
              <Card className={`border-2 ${riskInfo.colorClass}`}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">
                        NEWS2 Score
                      </p>
                      <p className="text-4xl font-bold">{vitals.news_score}</p>
                    </div>
                    <div className="text-right">
                      <Badge variant={riskInfo.variant} className="text-lg px-4 py-2">
                        {riskInfo.label}
                      </Badge>
                    </div>
                  </div>
                  <div className="mt-4 flex items-start gap-2">
                    <AlertTriangle className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
                    <p className="text-sm text-muted-foreground">
                      {riskInfo.recommendation}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Vitals Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {/* Heart Rate */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Heart className="h-4 w-4" />
                      Heart Rate
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{vitals.heart_rate}</p>
                    <p className="text-xs text-muted-foreground">bpm</p>
                  </CardContent>
                </Card>

                {/* Blood Pressure */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Activity className="h-4 w-4" />
                      Blood Pressure
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{vitals.blood_pressure}</p>
                    <p className="text-xs text-muted-foreground">mmHg</p>
                  </CardContent>
                </Card>

                {/* Temperature */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Thermometer className="h-4 w-4" />
                      Temperature
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{vitals.temperature}</p>
                    <p className="text-xs text-muted-foreground">°C</p>
                  </CardContent>
                </Card>

                {/* Respiratory Rate */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Wind className="h-4 w-4" />
                      Resp. Rate
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{vitals.respiratory_rate}</p>
                    <p className="text-xs text-muted-foreground">/min</p>
                  </CardContent>
                </Card>

                {/* Oxygen Saturation */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Droplets className="h-4 w-4" />
                      SpO₂
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {vitals.oxygen_saturation}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      % {vitals.oxygen_therapy && '(on O₂)'}
                    </p>
                  </CardContent>
                </Card>

                {/* Consciousness */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Brain className="h-4 w-4" />
                      Consciousness
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{vitals.consciousness}</p>
                    <p className="text-xs text-muted-foreground">AVPU</p>
                  </CardContent>
                </Card>
              </div>

              {/* Timestamp Footer */}
              <p className="text-xs text-muted-foreground text-center">
                Recorded: {new Date(vitals.timestamp).toLocaleString('en-GB', {
                  dateStyle: 'medium',
                  timeStyle: 'short',
                })}
              </p>
            </TabsContent>
          );
        })}
      </Tabs>
    </div>
  );
}

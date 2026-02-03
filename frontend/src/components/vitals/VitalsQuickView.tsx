/**
 * VitalsQuickView: Display patient vital signs with NEWS2 score
 * Shows 6-card grid layout with color-coded NEWS score banner
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Heart, Activity, Thermometer, Wind, Droplets, Brain } from 'lucide-react';
import type { VitalSignsResponse } from '@/api/types';

interface VitalsQuickViewProps {
  vitals: VitalSignsResponse;
}

export function VitalsQuickView({ vitals }: VitalsQuickViewProps) {
  // Determine NEWS score color and label
  const newsColor =
    vitals.news_score >= 7 ? 'destructive' :
    vitals.news_score >= 5 ? 'default' :
    'default';

  const newsLabel =
    vitals.news_score >= 7 ? 'High Risk' :
    vitals.news_score >= 5 ? 'Medium Risk' :
    'Low Risk';

  return (
    <div className="space-y-4">
      {/* NEWS Score Banner */}
      <Card className="border-2">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">NEWS2 Score</p>
              <p className="text-3xl font-bold">{vitals.news_score}</p>
            </div>
            <Badge variant={newsColor} className="text-lg px-4 py-2">
              {newsLabel}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Vitals Grid */}
      <div className="grid grid-cols-3 gap-4">
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

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Droplets className="h-4 w-4" />
              SpO₂
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{vitals.oxygen_saturation}</p>
            <p className="text-xs text-muted-foreground">
              % {vitals.oxygen_therapy && '(on O₂)'}
            </p>
          </CardContent>
        </Card>

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
    </div>
  );
}

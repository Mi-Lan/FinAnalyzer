import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MetricScores } from '@/types/financial';

interface ScoreCardProps {
  title: string;
  scores: MetricScores;
  recommendation?: 'BUY' | 'HOLD' | 'SELL';
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  return 'text-red-600';
}

function getRecommendationVariant(
  recommendation: string
): 'default' | 'secondary' | 'destructive' {
  switch (recommendation) {
    case 'BUY':
      return 'default';
    case 'HOLD':
      return 'secondary';
    case 'SELL':
      return 'destructive';
    default:
      return 'secondary';
  }
}

export function ScoreCard({ title, scores, recommendation }: ScoreCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        {recommendation && (
          <Badge variant={getRecommendationVariant(recommendation)}>
            {recommendation}
          </Badge>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="text-center">
            <div
              className={`text-4xl font-bold ${getScoreColor(scores.overall)}`}
            >
              {scores.overall}
            </div>
            <div className="text-sm text-muted-foreground">Overall Score</div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="flex justify-between">
                <span>Profitability</span>
                <span className={getScoreColor(scores.profitability)}>
                  {scores.profitability}
                </span>
              </div>
              <div className="mt-1 h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${scores.profitability}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between">
                <span>Growth</span>
                <span className={getScoreColor(scores.growth)}>
                  {scores.growth}
                </span>
              </div>
              <div className="mt-1 h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${scores.growth}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between">
                <span>Balance Sheet</span>
                <span className={getScoreColor(scores.balanceSheet)}>
                  {scores.balanceSheet}
                </span>
              </div>
              <div className="mt-1 h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${scores.balanceSheet}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between">
                <span>Capital Allocation</span>
                <span className={getScoreColor(scores.capitalAllocation)}>
                  {scores.capitalAllocation}
                </span>
              </div>
              <div className="mt-1 h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${scores.capitalAllocation}%` }}
                />
              </div>
            </div>

            <div className="col-span-2">
              <div className="flex justify-between">
                <span>Valuation</span>
                <span className={getScoreColor(scores.valuation)}>
                  {scores.valuation}
                </span>
              </div>
              <div className="mt-1 h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${scores.valuation}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

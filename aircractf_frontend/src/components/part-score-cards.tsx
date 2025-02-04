import { PartScoreType } from "@/app/dashboard/page";
import { Plane } from "lucide-react";

interface PartScoreCardsProps {
  score: PartScoreType | undefined;
  isLoading: boolean;
}

export function PartScoreCards({ score, isLoading }: PartScoreCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-white p-4 rounded-lg shadow animate-pulse h-32"
          >
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!score) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {Object.entries(score.scores).map(([planeType, stats]) => (
        <div
          key={planeType}
          className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <div className="flex justify-center mb-2">
            <Plane className="w-8 h-8 text-blue-600" />
          </div>
          <h3 className="text-base font-semibold mb-3">
            {planeType} Uçak için {score.part_type}lar
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between items-start">
              <span className="text-sm text-gray-600 max-w-[200px] whitespace-normal">
                {planeType} uçak üretiminde kullanılan {score.part_type} parça
                sayısı
              </span>
              <span className="font-medium text-blue-600 ml-2">
                {stats.used}
              </span>
            </div>
            <div className="flex justify-between items-start">
              <span className="text-sm text-gray-600 max-w-[200px] whitespace-normal">
                Kullanılmayan {score.part_type} parça sayısı
              </span>
              <span className="font-medium text-gray-600 ml-2">
                {stats.unused}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

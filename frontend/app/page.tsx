"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { MapPin, Search, Locate } from "lucide-react"
import { ResilienceGauge } from "@/components/resilience-gauge"
import { RecommendationsPanel } from "@/components/recommendations-panel"
import { DataVisualization } from "@/components/data-visualization"
import { WeatherIntegration } from "@/components/weather-integration"
import { CropRecommendationEngine } from "@/components/crop-recommendation-engine"
import { InputCostCalculator } from "@/components/input-cost-calculator"

// Kenyan counties data
const kenyanCounties = [
  "Baringo",
  "Bomet",
  "Bungoma",
  "Busia",
  "Elgeyo-Marakwet",
  "Embu",
  "Garissa",
  "Homa Bay",
  "Isiolo",
  "Kajiado",
  "Kakamega",
  "Kericho",
  "Kiambu",
  "Kilifi",
  "Kirinyaga",
  "Kisii",
  "Kisumu",
  "Kitui",
  "Kwale",
  "Laikipia",
  "Lamu",
  "Machakos",
  "Makueni",
  "Mandera",
  "Marsabit",
  "Meru",
  "Migori",
  "Mombasa",
  "Murang'a",
  "Nairobi",
  "Nakuru",
  "Nandi",
  "Narok",
  "Nyamira",
  "Nyandarua",
  "Nyeri",
  "Samburu",
  "Siaya",
  "Taita-Taveta",
  "Tana River",
  "Tharaka-Nithi",
  "Trans Nzoia",
  "Turkana",
  "Uasin Gishu",
  "Vihiga",
  "Wajir",
  "West Pokot",
]

export default function AgriAdaptDashboard() {
  const [selectedCounty, setSelectedCounty] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState("")
  const [showMap, setShowMap] = useState(false)
  const [showResilienceScore, setShowResilienceScore] = useState(false)
  const [resilienceData, setResilienceData] = useState({
    score: 0,
    confidence: 0,
  })

  const filteredCounties = kenyanCounties.filter((county) => county.toLowerCase().includes(searchTerm.toLowerCase()))

  const handleLocationDetection = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          // In a real app, you'd reverse geocode the coordinates
          // For demo purposes, we'll just set a default county
          setSelectedCounty("Nairobi")
        },
        (error) => {
          console.error("Error getting location:", error)
        },
      )
    }
  }

  const handleCheckResilienceScore = () => {
    setShowResilienceScore(true)

    const mockScores: { [key: string]: { score: number; confidence: number } } = {
      Nairobi: { score: 78, confidence: 85 },
      Mombasa: { score: 65, confidence: 78 },
      Kisumu: { score: 45, confidence: 72 },
      Nakuru: { score: 82, confidence: 90 },
      Eldoret: { score: 58, confidence: 80 },
    }

    const countyData = mockScores[selectedCounty] || {
      score: Math.floor(Math.random() * 100),
      confidence: Math.floor(Math.random() * 30) + 70,
    }

    setTimeout(() => {
      setResilienceData(countyData)
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-primary text-primary-foreground py-4 sm:py-6 px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-center mb-2 text-balance">
            Agri-Adapt AI Dashboard
          </h1>
          <p className="text-center text-primary-foreground/90 text-xs sm:text-sm md:text-base text-pretty">
            Check drought resilience scores for your maize crops
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-3 sm:p-4 space-y-4 sm:space-y-6">
        {/* County Selection Card */}
        <Card className="animate-fade-in">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
              <MapPin className="h-5 w-5 text-primary flex-shrink-0" />
              Select Your County
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 px-4 sm:px-6">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search for your county..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 min-h-[44px] touch-manipulation text-base"
              />
            </div>

            {/* County Dropdown */}
            <Select value={selectedCounty} onValueChange={setSelectedCounty}>
              <SelectTrigger className="w-full min-h-[44px] touch-manipulation text-base">
                <SelectValue placeholder="Choose your county" />
              </SelectTrigger>
              <SelectContent>
                {filteredCounties.map((county) => (
                  <SelectItem key={county} value={county} className="min-h-[44px] touch-manipulation">
                    {county}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                onClick={handleLocationDetection}
                variant="outline"
                className="flex-1 flex items-center gap-2 bg-transparent min-h-[44px] touch-manipulation text-sm"
              >
                <Locate className="h-4 w-4 flex-shrink-0" />
                Use Current Location
              </Button>
              <Button
                onClick={() => setShowMap(!showMap)}
                variant="outline"
                className="flex-1 min-h-[44px] touch-manipulation text-sm"
              >
                {showMap ? "Hide Map" : "Show Map"}
              </Button>
            </div>

            {/* Simple Map Placeholder */}
            {showMap && (
              <div className="mt-4 p-4 sm:p-6 bg-muted rounded-lg border-2 border-dashed border-border text-center animate-fade-in">
                <MapPin className="h-10 w-10 sm:h-12 sm:w-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground text-sm sm:text-base">
                  Interactive Kenya map would be displayed here
                </p>
                <p className="text-xs sm:text-sm text-muted-foreground mt-1">Click on your county to select it</p>
              </div>
            )}

            {/* Selected County Display */}
            {selectedCounty && (
              <div className="mt-4 p-4 bg-primary/10 rounded-lg border border-primary/20 animate-fade-in">
                <p className="text-xs sm:text-sm text-muted-foreground">Selected County:</p>
                <p className="text-base sm:text-lg font-semibold text-primary">{selectedCounty}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Next Steps */}
        {selectedCounty && !showResilienceScore && (
          <Card className="animate-fade-in">
            <CardContent className="pt-6 px-4 sm:px-6">
              <div className="text-center space-y-4">
                <div className="h-14 w-14 sm:h-16 sm:w-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                  <MapPin className="h-7 w-7 sm:h-8 sm:w-8 text-primary" />
                </div>
                <h3 className="text-lg sm:text-xl font-semibold text-foreground text-balance">
                  Great! You've selected {selectedCounty}
                </h3>
                <p className="text-muted-foreground text-sm sm:text-base text-pretty">
                  Now let's check the drought resilience score for your area
                </p>
                <Button
                  className="bg-primary hover:bg-primary/90 text-primary-foreground min-h-[44px] touch-manipulation px-6 text-sm sm:text-base"
                  onClick={handleCheckResilienceScore}
                >
                  Check Resilience Score
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Resilience Score Display */}
        {showResilienceScore && selectedCounty && (
          <>
            <ResilienceGauge
              score={resilienceData.score}
              confidence={resilienceData.confidence}
              county={selectedCounty}
            />
            <WeatherIntegration score={resilienceData.score} county={selectedCounty} />
            <CropRecommendationEngine score={resilienceData.score} county={selectedCounty} />
            <InputCostCalculator score={resilienceData.score} county={selectedCounty} />
            <RecommendationsPanel score={resilienceData.score} county={selectedCounty} />
            <DataVisualization score={resilienceData.score} county={selectedCounty} />
          </>
        )}
      </main>
    </div>
  )
}

"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { MapPin, Search, Locate, Loader2 } from "lucide-react"
import { ResilienceGauge } from "@/components/resilience-gauge"
import { RecommendationsPanel } from "@/components/recommendations-panel"
import { DataVisualization } from "@/components/data-visualization"
import { WeatherIntegration } from "@/components/weather-integration"
import { CropRecommendationEngine } from "@/components/crop-recommendation-engine"
import { InputCostCalculator } from "@/components/input-cost-calculator"

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Kenyan counties data - will be fetched from backend
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

// County coordinates for geolocation (simplified - in real app, use proper GIS data)
const COUNTY_COORDINATES: { [key: string]: { lat: number; lng: number; radius: number } } = {
  "Nairobi": { lat: -1.2921, lng: 36.8219, radius: 50 },
  "Mombasa": { lat: -4.0435, lng: 39.6682, radius: 40 },
  "Kisumu": { lat: -0.1022, lng: 34.7617, radius: 45 },
  "Nakuru": { lat: -0.3031, lng: 36.0800, radius: 35 },
  "Eldoret": { lat: 0.5204, lng: 35.2699, radius: 30 },
  "Thika": { lat: -1.0333, lng: 37.0833, radius: 25 },
  "Kakamega": { lat: 0.2833, lng: 34.7500, radius: 30 },
  "Kisii": { lat: -0.6833, lng: 34.7667, radius: 25 },
  "Kericho": { lat: -0.3667, lng: 35.2833, radius: 25 },
  "Nyeri": { lat: -0.4167, lng: 36.9500, radius: 25 },
  "Machakos": { lat: -1.5167, lng: 37.2667, radius: 30 },
  "Embu": { lat: -0.5333, lng: 37.4500, radius: 25 },
  "Meru": { lat: 0.0500, lng: 37.6500, radius: 30 },
  "Narok": { lat: -1.0833, lng: 35.8667, radius: 40 },
  "Kajiado": { lat: -1.8500, lng: 36.7833, radius: 35 },
  "Garissa": { lat: -0.4500, lng: 39.6500, radius: 50 },
  "Wajir": { lat: 1.7500, lng: 40.0500, radius: 60 },
  "Mandera": { lat: 3.9333, lng: 41.8500, radius: 70 },
  "Marsabit": { lat: 2.3333, lng: 37.9833, radius: 80 },
  "Isiolo": { lat: 0.3500, lng: 37.5833, radius: 45 },
  "Lamu": { lat: -2.2719, lng: 40.9020, radius: 35 },
  "Kilifi": { lat: -3.6333, lng: 39.8500, radius: 40 },
  "Kwale": { lat: -4.1833, lng: 39.4500, radius: 35 },
  "Taita-Taveta": { lat: -3.4000, lng: 38.3667, radius: 45 },
  "Tana River": { lat: -1.5000, lng: 40.0000, radius: 60 },
  "Bungoma": { lat: 0.5667, lng: 34.5667, radius: 30 },
  "Busia": { lat: 0.4667, lng: 34.1167, radius: 25 },
  "Vihiga": { lat: 0.0833, lng: 34.7167, radius: 25 },
  "Bomet": { lat: -0.7833, lng: 35.3333, radius: 25 },
  "Baringo": { lat: 0.4667, lng: 35.9667, radius: 35 },
  "Laikipia": { lat: 0.2000, lng: 36.8000, radius: 40 },
  "Nandi": { lat: 0.2000, lng: 35.1000, radius: 25 },
  "Uasin Gishu": { lat: 0.5167, lng: 35.2833, radius: 30 },
  "Trans Nzoia": { lat: 1.0167, lng: 34.9833, radius: 30 },
  "West Pokot": { lat: 1.2500, lng: 35.1167, radius: 35 },
  "Samburu": { lat: 1.1000, lng: 36.6833, radius: 45 },
  "Turkana": { lat: 3.1167, lng: 35.6000, radius: 80 },
  "Elgeyo-Marakwet": { lat: 0.5167, lng: 35.2833, radius: 30 },
  "Kirinyaga": { lat: -0.5000, lng: 37.3167, radius: 25 },
  "Murang'a": { lat: -0.7167, lng: 37.1500, radius: 25 },
  "Kiambu": { lat: -1.1667, lng: 36.8333, radius: 25 },
  "Nyandarua": { lat: -0.5333, lng: 36.4500, radius: 30 },
  "Kitui": { lat: -1.3667, lng: 38.0167, radius: 40 },
  "Makueni": { lat: -1.8000, lng: 37.6167, radius: 35 },
  "Tharaka-Nithi": { lat: -0.3000, lng: 37.6500, radius: 30 },
  "Migori": { lat: -1.0667, lng: 34.4667, radius: 30 },
  "Homa Bay": { lat: -0.5333, lng: 34.4500, radius: 30 },
  "Siaya": { lat: 0.0667, lng: 34.2833, radius: 25 },
  "Nyamira": { lat: -0.5667, lng: 34.9500, radius: 25 },
}

export default function AgriAdaptDashboard() {
  const [selectedCounty, setSelectedCounty] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState("")
  const [showMap, setShowMap] = useState(false)
  const [showResilienceScore, setShowResilienceScore] = useState(false)
  const [resilienceData, setResilienceData] = useState({
    score: 0,
    confidence: 0,
  })
  const [isLoading, setIsLoading] = useState(false)
  const [locationError, setLocationError] = useState<string>("")
  const [counties, setCounties] = useState<string[]>(kenyanCounties)

  // Fetch counties from backend on component mount
  useEffect(() => {
    fetchCounties()
  }, [])

  const fetchCounties = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/counties`)
      if (response.ok) {
        const data = await response.json()
        setCounties(data.counties || kenyanCounties)
      }
    } catch (error) {
      console.log("Using fallback counties list")
      // Keep using the hardcoded list if API fails
    }
  }

  const filteredCounties = counties.filter((county) =>
    county.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Calculate distance between two coordinates
  const calculateDistance = (lat1: number, lng1: number, lat2: number, lng2: number): number => {
    const R = 6371 // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180
    const dLng = (lng2 - lng1) * Math.PI / 180
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLng / 2) * Math.sin(dLng / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  // Find county based on coordinates
  const findCountyByCoordinates = (lat: number, lng: number): string | null => {
    let closestCounty: string | null = null
    let minDistance = Infinity

    for (const [county, coords] of Object.entries(COUNTY_COORDINATES)) {
      const distance = calculateDistance(lat, lng, coords.lat, coords.lng)
      if (distance <= coords.radius && distance < minDistance) {
        minDistance = distance
        closestCounty = county
      }
    }

    return closestCounty
  }

  const handleLocationDetection = () => {
    setIsLoading(true)
    setLocationError("")

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          const detectedCounty = findCountyByCoordinates(latitude, longitude)

          if (detectedCounty) {
            setSelectedCounty(detectedCounty)
            console.log(`Location detected: ${detectedCounty} County`)
          } else {
            setLocationError("Location detected but county not found. Please select manually.")
          }
          setIsLoading(false)
        },
        (error) => {
          console.error("Error getting location:", error)
          let errorMessage = "Unable to get your location."

          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = "Location access denied. Please enable location services."
              break
            case error.POSITION_UNAVAILABLE:
              errorMessage = "Location information unavailable."
              break
            case error.TIMEOUT:
              errorMessage = "Location request timed out."
              break
          }

          setLocationError(errorMessage)
          setIsLoading(false)
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        }
      )
    } else {
      setLocationError("Geolocation is not supported by your browser.")
      setIsLoading(false)
    }
  }

  const handleCheckResilienceScore = async () => {
    if (!selectedCounty) return

    setIsLoading(true)
    setShowResilienceScore(true)

    try {
      // For MVP, we'll use default environmental parameters for the county
      // In the future, this could be enhanced with real-time weather data
      const defaultParams = {
        rainfall: 800, // Default annual rainfall in mm
        soil_ph: 6.5,  // Default soil pH
        organic_carbon: 2.1 // Default organic carbon %
      }

      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...defaultParams,
          county: selectedCounty
        })
      })

      if (response.ok) {
        const data = await response.json()
        const prediction = data.prediction

        setResilienceData({
          score: prediction.resilience_score,
          confidence: prediction.confidence_score ? Math.round(prediction.confidence_score * 100) : 85
        })
      } else {
        // Fallback to mock data if API fails
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

        setResilienceData(countyData)
      }
    } catch (error) {
      console.error("Error fetching prediction:", error)
      // Fallback to mock data
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

      setResilienceData(countyData)
    } finally {
      setIsLoading(false)
    }
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
                disabled={isLoading}
                className="flex-1 flex items-center gap-2 bg-transparent min-h-[44px] touch-manipulation text-sm"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 flex-shrink-0 animate-spin" />
                ) : (
                  <Locate className="h-4 w-4 flex-shrink-0" />
                )}
                {isLoading ? "Detecting..." : "Use Current Location"}
              </Button>
              <Button
                onClick={() => setShowMap(!showMap)}
                variant="outline"
                className="flex-1 min-h-[44px] touch-manipulation text-sm"
              >
                {showMap ? "Hide Map" : "Show Map"}
              </Button>
            </div>

            {/* Location Error Display */}
            {locationError && (
              <div className="mt-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg animate-fade-in">
                <p className="text-destructive text-sm">{locationError}</p>
              </div>
            )}

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
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Checking...
                    </>
                  ) : (
                    "Check Resilience Score"
                  )}
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

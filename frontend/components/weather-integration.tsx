"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import {
  Cloud,
  CloudRain,
  Sun,
  Thermometer,
  Droplets,
  Wind,
  AlertTriangle,
  Bell,
  Calendar,
  TrendingUp,
  Snowflake,
  Eye,
} from "lucide-react"

interface WeatherIntegrationProps {
  county: string
  score: number
}

interface WeatherDay {
  date: string
  day: string
  high: number
  low: number
  humidity: number
  rainfall: number
  windSpeed: number
  condition: "sunny" | "cloudy" | "rainy" | "stormy"
  droughtRisk: "low" | "medium" | "high"
  plantingWindow: boolean
}

interface WeatherAlert {
  id: string
  type: "frost" | "drought" | "heavy_rain" | "temperature"
  severity: "low" | "medium" | "high"
  title: string
  description: string
  timestamp: string
  active: boolean
}

export function WeatherIntegration({ county, score }: WeatherIntegrationProps) {
  const [activeAlerts, setActiveAlerts] = useState<WeatherAlert[]>([])
  const [notificationsEnabled, setNotificationsEnabled] = useState(false)

  // Mock 7-day weather forecast
  const weatherForecast: WeatherDay[] = [
    {
      date: "2024-01-15",
      day: "Today",
      high: 28,
      low: 18,
      humidity: 65,
      rainfall: 0,
      windSpeed: 12,
      condition: "sunny",
      droughtRisk: "low",
      plantingWindow: true,
    },
    {
      date: "2024-01-16",
      day: "Tomorrow",
      high: 30,
      low: 20,
      humidity: 70,
      rainfall: 5,
      windSpeed: 8,
      condition: "cloudy",
      droughtRisk: "low",
      plantingWindow: true,
    },
    {
      date: "2024-01-17",
      day: "Wed",
      high: 32,
      low: 22,
      humidity: 75,
      rainfall: 15,
      windSpeed: 15,
      condition: "rainy",
      droughtRisk: "low",
      plantingWindow: false,
    },
    {
      date: "2024-01-18",
      day: "Thu",
      high: 29,
      low: 19,
      humidity: 68,
      rainfall: 2,
      windSpeed: 10,
      condition: "cloudy",
      droughtRisk: "medium",
      plantingWindow: true,
    },
    {
      date: "2024-01-19",
      day: "Fri",
      high: 35,
      low: 25,
      humidity: 55,
      rainfall: 0,
      windSpeed: 18,
      condition: "sunny",
      droughtRisk: "high",
      plantingWindow: false,
    },
    {
      date: "2024-01-20",
      day: "Sat",
      high: 33,
      low: 23,
      humidity: 60,
      rainfall: 8,
      windSpeed: 14,
      condition: "cloudy",
      droughtRisk: "medium",
      plantingWindow: true,
    },
    {
      date: "2024-01-21",
      day: "Sun",
      high: 27,
      low: 17,
      humidity: 72,
      rainfall: 12,
      windSpeed: 9,
      condition: "rainy",
      droughtRisk: "low",
      plantingWindow: true,
    },
  ]

  // Mock weather alerts
  const mockAlerts: WeatherAlert[] = [
    {
      id: "1",
      type: "temperature",
      severity: "high",
      title: "High Temperature Alert",
      description: "Temperatures expected to reach 35°C on Friday. Consider additional irrigation.",
      timestamp: "2024-01-15T08:00:00Z",
      active: true,
    },
    {
      id: "2",
      type: "drought",
      severity: "medium",
      title: "Drought Risk Increasing",
      description: "Low rainfall expected for next 3 days. Monitor soil moisture levels closely.",
      timestamp: "2024-01-15T06:30:00Z",
      active: true,
    },
  ]

  useEffect(() => {
    setActiveAlerts(mockAlerts)
  }, [])

  const getWeatherIcon = (condition: string) => {
    switch (condition) {
      case "sunny":
        return <Sun className="h-6 w-6 text-yellow-500" />
      case "cloudy":
        return <Cloud className="h-6 w-6 text-gray-500" />
      case "rainy":
        return <CloudRain className="h-6 w-6 text-blue-500" />
      case "stormy":
        return <CloudRain className="h-6 w-6 text-purple-500" />
      default:
        return <Sun className="h-6 w-6 text-yellow-500" />
    }
  }

  const getDroughtRiskColor = (risk: string) => {
    switch (risk) {
      case "low":
        return "bg-green-100 text-green-800"
      case "medium":
        return "bg-orange-100 text-orange-800"
      case "high":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "frost":
        return <Snowflake className="h-4 w-4" />
      case "drought":
        return <Sun className="h-4 w-4" />
      case "heavy_rain":
        return <CloudRain className="h-4 w-4" />
      case "temperature":
        return <Thermometer className="h-4 w-4" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  const getAlertColor = (severity: string) => {
    switch (severity) {
      case "low":
        return "border-yellow-200 bg-yellow-50 text-yellow-800"
      case "medium":
        return "border-orange-200 bg-orange-50 text-orange-800"
      case "high":
        return "border-red-200 bg-red-50 text-red-800"
      default:
        return "border-gray-200 bg-gray-50 text-gray-800"
    }
  }

  const enableNotifications = async () => {
    if ("Notification" in window) {
      const permission = await Notification.requestPermission()
      setNotificationsEnabled(permission === "granted")
    }
  }

  // Calculate seasonal rainfall comparison
  const currentMonthRainfall = weatherForecast.reduce((sum, day) => sum + day.rainfall, 0)
  const seasonalExpected = 85 // Mock seasonal average
  const rainfallComparison = (currentMonthRainfall / seasonalExpected) * 100

  return (
    <Card className="animate-fade-in">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
          <Cloud className="h-5 w-5 text-primary flex-shrink-0" />
          <span className="text-balance">Weather Integration - {county}</span>
        </CardTitle>
        <p className="text-xs sm:text-sm text-muted-foreground">Real-time weather data and agricultural insights</p>
      </CardHeader>
      <CardContent className="px-3 sm:px-6">
        <Tabs defaultValue="forecast" className="w-full">
          <TabsList className="grid w-full grid-cols-4 h-12 sm:h-10 mb-6">
            <TabsTrigger
              value="forecast"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Eye className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Forecast</span>
            </TabsTrigger>
            <TabsTrigger
              value="alerts"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm relative"
            >
              <Bell className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Alerts</span>
              {activeAlerts.length > 0 && (
                <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs bg-red-500 text-white">
                  {activeAlerts.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger
              value="planting"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Calendar className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Planting</span>
            </TabsTrigger>
            <TabsTrigger
              value="rainfall"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Droplets className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Rainfall</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="forecast" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  7-Day Weather Forecast
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Detailed weather conditions with drought risk indicators
                </p>
              </div>

              <div className="grid gap-3">
                {weatherForecast.map((day, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg min-h-[80px] touch-manipulation"
                  >
                    <div className="flex-shrink-0">{getWeatherIcon(day.condition)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-sm text-foreground">{day.day}</h4>
                        <Badge className={`text-xs ${getDroughtRiskColor(day.droughtRisk)}`}>
                          {day.droughtRisk} risk
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Thermometer className="h-3 w-3" />
                          {day.high}°/{day.low}°C
                        </div>
                        <div className="flex items-center gap-1">
                          <Droplets className="h-3 w-3" />
                          {day.rainfall}mm
                        </div>
                        <div className="flex items-center gap-1">
                          <Wind className="h-3 w-3" />
                          {day.windSpeed}km/h
                        </div>
                        <div className="flex items-center gap-1">
                          <Eye className="h-3 w-3" />
                          {day.humidity}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="alerts" className="mt-0">
            <div className="space-y-4">
              <div className="flex items-center justify-between px-1">
                <div>
                  <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                    Weather Alerts
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-foreground">
                    Critical weather notifications for your area
                  </p>
                </div>
                <Button
                  onClick={enableNotifications}
                  variant={notificationsEnabled ? "default" : "outline"}
                  size="sm"
                  className="min-h-[44px] touch-manipulation text-xs sm:text-sm"
                >
                  <Bell className="h-4 w-4 mr-2" />
                  {notificationsEnabled ? "Enabled" : "Enable"}
                </Button>
              </div>

              {activeAlerts.length === 0 ? (
                <div className="text-center py-8">
                  <Bell className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground text-sm">No active weather alerts</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {activeAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`border rounded-lg p-4 ${getAlertColor(alert.severity)} min-h-[80px] touch-manipulation`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 mt-1">{getAlertIcon(alert.type)}</div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-sm mb-1">{alert.title}</h4>
                          <p className="text-xs text-pretty mb-2">{alert.description}</p>
                          <p className="text-xs opacity-75">{new Date(alert.timestamp).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="planting" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Planting Window Optimizer
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Optimal planting times based on weather patterns
                </p>
              </div>

              <div className="grid gap-3">
                {weatherForecast.map((day, index) => (
                  <div
                    key={index}
                    className={`flex items-center justify-between p-4 rounded-lg border min-h-[60px] touch-manipulation ${
                      day.plantingWindow ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Calendar className={`h-5 w-5 ${day.plantingWindow ? "text-green-600" : "text-red-600"}`} />
                      <div>
                        <h4 className="font-medium text-sm text-foreground">{day.day}</h4>
                        <p className="text-xs text-muted-foreground">
                          {day.high}°C, {day.rainfall}mm rain
                        </p>
                      </div>
                    </div>
                    <Badge
                      className={`text-xs ${
                        day.plantingWindow ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                      }`}
                    >
                      {day.plantingWindow ? "Good" : "Poor"}
                    </Badge>
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 bg-primary/10 rounded-lg border border-primary/20">
                <h4 className="font-semibold text-sm text-foreground mb-2 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  Planting Recommendations
                </h4>
                <ul className="space-y-2 text-xs sm:text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                    Best planting days: Today, Tomorrow, Thursday, Saturday, Sunday
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                    Avoid planting: Wednesday (heavy rain), Friday (high temperature)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                    Consider drought-resistant varieties for Friday's conditions
                  </li>
                </ul>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="rainfall" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Rainfall Tracking
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Current rainfall vs. seasonal expectations
                </p>
              </div>

              <div className="space-y-6">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-sm text-foreground">7-Day Rainfall Total</h4>
                    <span className="text-lg font-bold text-primary">{currentMonthRainfall}mm</span>
                  </div>
                  <Progress value={(currentMonthRainfall / 100) * 100} className="h-3" />
                  <p className="text-xs text-muted-foreground mt-2">Expected for this period: {seasonalExpected}mm</p>
                </div>

                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-sm text-foreground">Seasonal Comparison</h4>
                    <span
                      className={`text-lg font-bold ${
                        rainfallComparison >= 80
                          ? "text-green-600"
                          : rainfallComparison >= 60
                            ? "text-orange-600"
                            : "text-red-600"
                      }`}
                    >
                      {Math.round(rainfallComparison)}%
                    </span>
                  </div>
                  <Progress
                    value={rainfallComparison}
                    className={`h-3 ${
                      rainfallComparison >= 80
                        ? "[&>div]:bg-green-500"
                        : rainfallComparison >= 60
                          ? "[&>div]:bg-orange-500"
                          : "[&>div]:bg-red-500"
                    }`}
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    {rainfallComparison >= 80
                      ? "Above average rainfall - good for crops"
                      : rainfallComparison >= 60
                        ? "Below average - monitor soil moisture"
                        : "Significantly below average - irrigation recommended"}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Droplets className="h-4 w-4 text-blue-600" />
                      <h4 className="font-medium text-sm text-blue-900">This Week</h4>
                    </div>
                    <p className="text-2xl font-bold text-blue-600">{currentMonthRainfall}mm</p>
                    <p className="text-xs text-blue-700">Total rainfall</p>
                  </div>
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <h4 className="font-medium text-sm text-green-900">Forecast</h4>
                    </div>
                    <p className="text-2xl font-bold text-green-600">
                      {weatherForecast.slice(0, 3).reduce((sum, day) => sum + day.rainfall, 0)}mm
                    </p>
                    <p className="text-xs text-green-700">Next 3 days</p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

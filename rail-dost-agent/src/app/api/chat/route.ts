import { NextRequest, NextResponse } from 'next/server';

// Station codes and city names mapping
const STATION_MAP: Record<string, string> = {
  'ndls': 'New Delhi',
  'csmt': 'Mumbai CST',
  'sbc': 'Bangalore City',
  'hwh': 'Howrah',
  'mas': 'Chennai Central',
  'ghy': 'Guwahati',
  'bbs': 'Bhubaneswar',
  'jp': 'Jaipur',
  'lko': 'Lucknow',
  'pnbe': 'Patna',
  'cgb': 'Vijayawada',
  'stp': 'Surat',
  'dbl': 'Dibrugarh',
  'rnc': 'Ranchi',
  'bkn': 'Bikaner',
};

// Mock train data
const MOCK_TRAINS = [
  {
    trainNumber: '12002',
    trainName: 'Bhopal Shatabdi Express',
    from: 'NDLS',
    to: 'Bhopal',
    departure: '06:00',
    arrival: '14:30',
    duration: '8h 30m',
    classes: ['1A', '2A', 'CC', 'SL'],
  },
  {
    trainNumber: '12952',
    trainName: 'Mumbai Rajdhani',
    from: 'CSMT',
    to: 'New Delhi',
    departure: '16:00',
    arrival: '08:30',
    duration: '16h 30m',
    classes: ['1A', '2A', '3A'],
  },
  {
    trainNumber: '12559',
    trainName: 'Garib Rath Exp',
    from: 'SBC',
    to: 'NDLS',
    departure: '22:00',
    arrival: '06:15',
    duration: '8h 15m',
    classes: ['3A', 'SL'],
  },
  {
    trainNumber: '12302',
    trainName: 'Howrah Mail',
    from: 'HWH',
    to: 'NDLS',
    departure: '23:55',
    arrival: '19:40',
    duration: '19h 45m',
    classes: ['1A', '2A', '3A', 'SL'],
  },
  {
    trainNumber: '12759',
    trainName: 'Charminar Express',
    from: 'MAS',
    to: 'HWH',
    departure: '14:00',
    arrival: '14:45',
    duration: '24h 45m',
    classes: ['2A', '3A', 'SL'],
  },
  {
    trainNumber: '15636',
    trainName: 'Kamakhya Express',
    from: 'GHY',
    to: 'NDLS',
    departure: '18:30',
    arrival: '21:05',
    duration: '26h 35m',
    classes: ['2A', '3A', 'SL'],
  },
  {
    trainNumber: '18477',
    trainName: 'Puri Express',
    from: 'BBS',
    to: 'NDLS',
    departure: '06:00',
    arrival: '20:00',
    duration: '14h 00m',
    classes: ['2A', '3A', 'SL'],
  },
  {
    trainNumber: '12924',
    trainName: 'Diwana Express',
    from: 'JP',
    to: 'CSMT',
    departure: '19:00',
    arrival: '16:00',
    duration: '21h 00m',
    classes: ['2A', '3A', 'SL'],
  },
  {
    trainNumber: '12531',
    trainName: 'Lichchavi Express',
    from: 'LKO',
    to: 'PNBE',
    departure: '07:00',
    arrival: '11:30',
    duration: '4h 30m',
    classes: ['CC', '2A'],
  },
  {
    trainNumber: '12703',
    trainName: 'Falaknuma Express',
    from: 'CGB',
    to: 'MAS',
    departure: '16:00',
    arrival: '11:00',
    duration: '19h 00m',
    classes: ['2A', '3A', 'SL'],
  },
];

interface Train {
  trainNumber: string;
  trainName: string;
  from: string;
  to: string;
  departure: string;
  arrival: string;
  duration: string;
  classes: string[];
}

function searchTrains(query: string): { trains: Train[]; message: string } {
  const q = query.toLowerCase();
  
  // Extract station codes from query
  const foundStations: string[] = [];
  for (const [code, name] of Object.entries(STATION_MAP)) {
    if (q.includes(code) || q.includes(name.toLowerCase())) {
      foundStations.push(code.toUpperCase());
    }
  }
  
  // If no stations found, return some trains
  if (foundStations.length === 0) {
    // Return random selection of trains
    const shuffled = [...MOCK_TRAINS].sort(() => 0.5 - Math.random());
    return {
      trains: shuffled.slice(0, 4),
      message: "Here are some popular trains for you! Let me know your source and destination for more options.",
    };
  }
  
  // Filter trains based on station codes
  const filtered = MOCK_TRAINS.filter(train => 
    foundStations.some(station => 
      train.from.includes(station) || train.to.includes(station)
    )
  );
  
  const trains = filtered.length > 0 ? filtered.slice(0, 5) : MOCK_TRAINS.slice(0, 3);
  const stationNames = foundStations.map(s => STATION_MAP[s.toLowerCase()] || s).join(' and ');
  
  return {
    trains,
    message: `I found ${trains.length} trains going through ${stationNames}. Here are the options:`,
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message } = body;
    
    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }
    
    // Extract trains based on the message
    const result = searchTrains(message);
    
    // Return the response
    return NextResponse.json({
      success: true,
      message: result.message,
      trains: result.trains,
      query: message,
    });
    
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}

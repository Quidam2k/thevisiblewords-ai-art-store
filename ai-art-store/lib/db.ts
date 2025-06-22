// Database connection and utilities
import { PrismaClient } from '@prisma/client'

declare global {
  var prisma: PrismaClient | undefined
}

export const db = globalThis.prisma || new PrismaClient()

if (process.env.NODE_ENV !== 'production') {
  globalThis.prisma = db
}

// Database utility functions
export async function connectToDatabase() {
  try {
    await db.$connect()
    console.log('Connected to database')
  } catch (error) {
    console.error('Database connection error:', error)
    throw error
  }
}

export async function disconnectFromDatabase() {
  try {
    await db.$disconnect()
    console.log('Disconnected from database')
  } catch (error) {
    console.error('Database disconnection error:', error)
  }
}
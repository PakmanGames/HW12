import { NextResponse } from "next/server";
import { db } from "~/server/db";
import * as schema from "~/server/db/schema";
import { desc, eq, sql } from "drizzle-orm";

export async function POST(request: Request, { params }: { params: { id: string } }) {
    try {
        // Update the error to mark it as resolved
        const updated = await db
            .update(schema.errors)
            .set({ 
                resolved: true,
                resolvedAt: sql`NOW()`
            })
            .where(eq(schema.errors.id, parseInt(params.id)))
            .returning();

        if (updated.length === 0) {
            return NextResponse.json({ error: "Error not found" }, { status: 404 });
        }

        return NextResponse.json(updated[0], { status: 200 });
    } catch (error) {
        console.error("Error resolving incident:", error);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}
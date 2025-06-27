/*
  Warnings:

  - A unique constraint covering the columns `[companyId,year,period,type]` on the table `FinancialData` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `type` to the `FinancialData` table without a default value. This is not possible if the table is not empty.

*/
-- DropIndex
DROP INDEX "FinancialData_companyId_year_period_key";

-- AlterTable
ALTER TABLE "FinancialData" ADD COLUMN     "type" TEXT NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "FinancialData_companyId_year_period_type_key" ON "FinancialData"("companyId", "year", "period", "type");

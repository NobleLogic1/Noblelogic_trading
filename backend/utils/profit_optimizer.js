class ProfitOptimizer {
    static calculateTimeBasedTarget(timeBlocks, baseTarget) {
        const currentHour = new Date().getUTCHours();
        const currentBlock = timeBlocks.find(block => 
            currentHour >= block.start && currentHour < block.end
        );
        
        return baseTarget * (currentBlock?.targetMultiplier || 1.0);
    }

    static updateProfitScaling(profitTargets, dailyProfit) {
        const scaling = profitTargets.profitScaling;
        if (!scaling.enabled) return profitTargets.daily;

        // Check if daily target was met
        if (dailyProfit >= profitTargets.daily) {
            scaling.consecutiveHits++;
            scaling.consecutiveMisses = 0;
            
            // Scale up target after consistent success
            if (scaling.consecutiveHits >= scaling.scaleUpThreshold) {
                const newTarget = Math.min(
                    profitTargets.daily * scaling.scalingFactor,
                    scaling.maxDailyTarget
                );
                profitTargets.daily = newTarget;
                scaling.consecutiveHits = 0;
                console.log(`Daily target increased to: $${newTarget.toFixed(2)}`);
            }
        } else {
            scaling.consecutiveMisses++;
            scaling.consecutiveHits = 0;
            
            // Scale down target after consistent misses
            if (scaling.consecutiveMisses >= scaling.scaleDownThreshold) {
                const newTarget = Math.max(
                    profitTargets.daily * scaling.reductionFactor,
                    scaling.minDailyTarget
                );
                profitTargets.daily = newTarget;
                scaling.consecutiveMisses = 0;
                console.log(`Daily target reduced to: $${newTarget.toFixed(2)}`);
            }
        }
        
        return profitTargets.daily;
    }

    static calculateOptimalTradeFrequency(timeBlock, marketConditions) {
        // Base frequency on time block multiplier
        let baseFrequency = Math.round(60 / timeBlock.targetMultiplier);
        
        // Adjust for market conditions
        if (marketConditions.volatility > 0.02) {
            baseFrequency = Math.max(30, baseFrequency * 0.8); // More frequent in volatile markets
        } else if (marketConditions.volatility < 0.005) {
            baseFrequency = Math.min(120, baseFrequency * 1.2); // Less frequent in stable markets
        }
        
        return baseFrequency;
    }
}

module.exports = ProfitOptimizer;
export default function FilterBar({
    filters,
    locationOptions,
    cuisineOptions,
    onChange,
    onReset,
}) {
    return (
        <section className="filter-bar" aria-label="Restaurant filters">
            <div className="filter-field">
                <label htmlFor="location-filter">Location</label>
                <select
                    id="location-filter"
                    value={filters.location}
                    onChange={(event) => onChange("location", event.target.value)}
                >
                    <option value="">All locations</option>
                    {locationOptions.map((location) => (
                        <option key={location} value={location}>
                            {location}
                        </option>
                    ))}
                </select>
            </div>

            <div className="filter-field">
                <label htmlFor="cuisine-filter">Cuisine</label>
                <select
                    id="cuisine-filter"
                    value={filters.cuisine}
                    onChange={(event) => onChange("cuisine", event.target.value)}
                >
                    <option value="">All cuisines</option>
                    {cuisineOptions.map((cuisine) => (
                        <option key={cuisine} value={cuisine}>
                            {cuisine}
                        </option>
                    ))}
                </select>
            </div>

            <div className="filter-field">
                <label htmlFor="max-fee-filter">Max delivery fee</label>
                <input
                    id="max-fee-filter"
                    type="number"
                    min="0"
                    step="0.5"
                    placeholder="e.g. 5"
                    value={filters.maxFee}
                    onChange={(event) => onChange("maxFee", event.target.value)}
                />
            </div>

            <button type="button" className="reset-filters-button" onClick={onReset}>
                Reset
            </button>
        </section>
    );
}

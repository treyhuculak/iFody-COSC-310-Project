import { useState } from "react";

function defaultGetItemKey(item, index) {
    if (item?.id !== undefined && item?.id !== null) {
        return item.id;
    }

    if (item?.name) {
        return `${item.name}-${index}`;
    }

    return String(index);
}

function defaultGetPrimaryText(item) {
    return item?.name || "Unknown item";
}

export default function SearchDropdown({
    inputId = "global-search",
    label,
    query,
    onQueryChange,
    results,
    isLoading,
    onSelect,
    placeholder = "Search",
    loadingText = "Searching...",
    emptyText = "No results found.",
    className = "",
    getItemKey = defaultGetItemKey,
    getItemPrimaryText = defaultGetPrimaryText,
    getItemSecondaryText,
}) {
    const [isOpen, setIsOpen] = useState(false);
    const showDropdown = isOpen && query.trim().length > 0;

    return (
        <div className={`search-dropdown-component ${className}`.trim()}>
            {label && (
                <label htmlFor={inputId} className="search-dropdown-label">
                    {label}
                </label>
            )}

            <div className="search-dropdown-input-wrap">
                <input
                    id={inputId}
                    className="search-dropdown-input"
                    type="search"
                    value={query}
                    placeholder={placeholder}
                    autoComplete="off"
                    onFocus={() => setIsOpen(true)}
                    onBlur={() => {
                        setTimeout(() => {
                            setIsOpen(false);
                        }, 120);
                    }}
                    onChange={(event) => {
                        onQueryChange(event.target.value);
                        setIsOpen(true);
                    }}
                />

                {showDropdown && (
                    <div className="search-dropdown-panel" role="listbox">
                        {isLoading ? (
                            <div className="search-dropdown-status">{loadingText}</div>
                        ) : results.length > 0 ? (
                            results.map((item, index) => {
                                const primaryText = getItemPrimaryText(item);
                                const secondaryText = getItemSecondaryText
                                    ? getItemSecondaryText(item)
                                    : "";

                                return (
                                    <button
                                        type="button"
                                        className="search-dropdown-result-item"
                                        key={getItemKey(item, index)}
                                        onMouseDown={() => onSelect(item)}
                                    >
                                        <span>{primaryText}</span>
                                        {secondaryText ? <small>{secondaryText}</small> : null}
                                    </button>
                                );
                            })
                        ) : (
                            <div className="search-dropdown-status">{emptyText}</div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

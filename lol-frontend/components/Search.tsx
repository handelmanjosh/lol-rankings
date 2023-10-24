
import { useState } from "react";
type SearchProps = {
    onSearch: (s: string) => any,
    data: { id: string; }[];
    placeholder: string;
};


export default function Search({ onSearch, data, placeholder }: SearchProps) {
    const [value, setValue] = useState('');
    const [matchedIds, setMatchedIds] = useState<any[]>([]);

    const change = (e: React.ChangeEvent<HTMLInputElement>) => {
        const inputValue = e.target.value;
        setValue(inputValue);
        // Filtering the players based on the input value
        const matched = data.filter((point: any) => point.id.includes(inputValue));
        setMatchedIds(matched);
    };
    const search = () => {
        value && onSearch(value);
        setMatchedIds([]);
    };
    return (
        <div className="relative">
            <div className="flex flex-row justify-center items-center gap-2">
                <input
                    value={value}
                    placeholder={placeholder}
                    onChange={change}
                    className="appearance-none bg-gray-200 outline-none p-2 focus:border-black focus:border rounded-md"
                />
                <button onClick={search} className="bg-gray-200 hover:brightness-90 active:brightness-75 rounded-md p-2">Search</button>
            </div>
            {matchedIds.length > 0 && (
                <div className="absolute top-full mt-2 w-full bg-white border border-gray-300 rounded shadow">
                    {matchedIds.map(point => (
                        <div onClick={() => setValue(point.id)} key={point.id} className="p-2 text-black hover:bg-gray-200">
                            {`${point.id} - ${point.name || point.handle}`}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

type BasicButtonProps = {
    text: string;
    onClick: () => any;
};
export default function BasicButton({ text, onClick }: BasicButtonProps) {
    return (
        <button onClick={onClick} className="rounded-md bg-gray-200 py-2 px-4 hover:brightness-90 active:brightness-75">
            {text}
        </button>
    );
}
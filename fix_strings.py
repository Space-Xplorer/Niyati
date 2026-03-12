import os

filepath = r"c:\Users\mahes\OneDrive\Desktop\Projects\Projects_Personal\Niyati\frontend\src\app\upload\page.tsx"

with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    'ðŸ“¥': '📥',
    'ðŸ•¸ï¸ ': '🕸️',
    'ðŸ” ': '🔍',
    'ðŸ“Š': '📊',
    'ðŸ“ ': '💡',
    'ðŸ§¾': '🧾',
    'ðŸš›': '🚛',
    'ðŸ ¢': '🏢',
    'ðŸ“…': '📅',
    'ðŸ›’': '🛒',
    'ðŸ’°': '💰',
    'âš™ï¸ ': '⚙️',
    'âœ…': '✅',
    'âš¡': '⚡',
    'âš ï¸ ': '⚠️',
    'ðŸ¤–': '🤖',
    'ðŸ”„': '🔄',
    'ðŸ‘»': '👻',
    'ðŸ’¸': '💸',
    'ðŸ•µï¸ ': '🕵️',
    'â€”': '—',
    'â‚¹': '₹',
    'â†’': '→',
    'â€': '—' # fallbacks
}

for k, v in replacements.items():
    text = text.replace(k, v)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

print("Mojibake characters substituted successfully!")

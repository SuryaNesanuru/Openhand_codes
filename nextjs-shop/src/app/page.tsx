import { playfair } from "./layout";

interface Product {
  id: string;
  name: string;
  price: number;
  brand: string;
  category: string;
  available: boolean;
  description: string;
}

async function getProducts(query?: string): Promise<Product[]> {
  const allProducts: Product[] = [
    { id: "prod_001", name: "Nike Air Zoom Pegasus 39", price: 89.99, brand: "Nike", category: "running-shoes", available: true, description: "Lightweight running shoes" },
    { id: "prod_002", name: "Adidas Ultraboost 22", price: 95.00, brand: "Adidas", category: "running-shoes", available: true, description: "Premium running shoes" },
    { id: "prod_005", name: "Sony WH-1000XM5", price: 349.99, brand: "Sony", category: "headphones", available: true, description: "Noise cancellation" },
    { id: "prod_006", name: "Apple AirPods Pro 2", price: 249.00, brand: "Apple", category: "headphones", available: true, description: "Spatial Audio" },
    { id: "prod_007", name: "Jabra Elite 75t", price: 49.99, brand: "Jabra", category: "headphones", available: true, description: "Wireless earbuds" },
    { id: "prod_008", name: "Lululemon Align Yoga Pants", price: 68.00, brand: "Lululemon", category: "yoga-pants", available: true, description: "Nulu fabric" },
    { id: "prod_009", name: "Athleta Salutation Yoga Pants", price: 44.95, brand: "Athleta", category: "yoga-pants", available: true, description: "Hidden pocket" },
    { id: "prod_010", name: "Apple MacBook Air M2", price: 1099.00, brand: "Apple", category: "laptops", available: true, description: "M2 chip" },
    { id: "prod_003", name: "Apple iPhone 14 Pro", price: 999.00, brand: "Apple", category: "smartphones", available: true, description: "48MP camera" },
    { id: "prod_015", name: "Apple Watch Series 8", price: 399.00, brand: "Apple", category: "wearables", available: true, description: "Temperature sensing" }
  ];
  if (!query) return allProducts.slice(0, 6);
  const q = query.toLowerCase();
  return allProducts.filter(p => p.name.toLowerCase().includes(q) || p.brand.toLowerCase().includes(q) || p.category.includes(q));
}

export default async function Home({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const params = await searchParams;
  const query = params?.q || "";
  const products = await getProducts(query);
  
  const suggestions = ["running shoes", "wireless headphones", "yoga pants", "smartphones", "Apple products"];

  return (
    <div className="min-h-screen bg-[#fafaf9]">
      <header className="sticky top-0 z-50 bg-[#fafaf9]/80 backdrop-blur-md border-b border-[#e7e5e4]">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className={playfair.className + " text-2xl font-semibold tracking-tight"}>LUXE</h1>
          <nav className="flex items-center gap-6 text-sm text-[#57534e]">
            <a href="#" className="hover:text-[#1c1917]">Shop</a>
            <a href="#" className="hover:text-[#1c1917]">Collections</a>
            <a href="#" className="hover:text-[#1c1917]">About</a>
          </nav>
        </div>
      </header>

      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className={playfair.className + " text-5xl md:text-6xl font-semibold text-[#1c1917] mb-6"}>Find what you love</h2>
          <p className="text-lg text-[#57534e] mb-10">Our AI assistant curates the perfect selection for you</p>
          <form method="get" className="relative max-w-xl mx-auto">
            <input type="text" name="q" defaultValue={query} placeholder="Try: running shoes under 100" className="w-full px-6 py-4 text-lg bg-white border border-[#e7e5e4] rounded-full outline-none focus:border-[#b91c1c] transition-all placeholder:text-[#a8a29e]" />
            <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-[#1c1917] text-white rounded-full hover:bg-[#b91c1c]">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </button>
          </form>
          <div className="flex flex-wrap justify-center gap-2 mt-6">
            {suggestions.map((s) => (
              <a key={s} href={"?q=" + encodeURIComponent(s)} className="px-4 py-2 text-sm bg-white border border-[#e7e5e4] rounded-full text-[#57534e] hover:border-[#b91c1c] hover:text-[#b91c1c] transition-colors">{s}</a>
            ))}
          </div>
        </div>
      </section>

      {products.length > 0 && (
        <section className="py-12 px-6 bg-white">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <h3 className={playfair.className + " text-2xl font-semibold"}>{query ? "Results for \"" + query + "\"" : "Featured"}</h3>
              <span className="text-sm text-[#57534e]">{products.length} products</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map((product) => (
                <a key={product.id} href={"#product-" + product.id} className="group block">
                  <div className="aspect-square bg-[#f5f5f4] rounded-lg mb-4 overflow-hidden relative flex items-center justify-center text-6xl">
                    {!product.available && <span className="absolute top-3 left-3 px-2 py-1 text-xs bg-[#1c1917] text-white rounded">Sold Out</span>}
                    {getCategoryEmoji(product.category)}
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-[#a8a29e] uppercase tracking-wide">{product.brand}</p>
                    <h4 className="font-medium text-[#1c1917] group-hover:text-[#b91c1c] transition-colors">{product.name}</h4>
                    <p className="text-[#b91c1c] font-semibold">${product.price.toFixed(2)}</p>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>
      )}

      {query && products.length === 0 && (
        <section className="py-20 px-6">
          <div className="max-w-xl mx-auto text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className={playfair.className + " text-2xl font-semibold mb-2"}>No results found</h3>
            <p className="text-[#57534e]">Try different keywords</p>
          </div>
        </section>
      )}

      <footer className="py-12 px-6 border-t border-[#e7e5e4] mt-20">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <p className={playfair.className + " text-xl font-semibold"}>LUXE</p>
          <p className="text-sm text-[#57534e]">Curated shopping experience powered by AI</p>
        </div>
      </footer>
    </div>
  );
}

function getCategoryEmoji(category: string): string {
  const map: Record<string, string> = { "running-shoes": "👟", "headphones": "🎧", "smartphones": "📱", "yoga-pants": "👖", "laptops": "💻", "wearables": "⌚", "gaming": "🎮", "kitchen": "🍳", "home": "🏠", "audio": "🔊" };
  return map[category] || "📦";
}
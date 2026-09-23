import React, { useState, useMemo } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  FlatList,
  Image,
  Linking,
  SafeAreaView,
  StatusBar,
  ScrollView,
  Modal,
  Dimensions,
} from 'react-native';

const { width } = Dimensions.get('window');

// داتای سەرەکی و دەوڵەمەندی شاری کەرکووک بۆ ٨ بەشەکە
const ALL_PLACES = [
  // ١ و ٤. شوێنە مێژووییەکان
  {
    id: 'h1',
    name: 'قەڵای دێرینی کەرکووک',
    category: 'historic',
    catName: 'شوێنەوار',
    rating: '4.9',
    address: 'سەنتەری شاری کەرکووک',
    desc: 'کۆنترین شوێنەواری مێژوویی شارەکە کە مێژووەکەی بۆ زیاتر لە ٥٠٠٠ ساڵ دەگەڕێتەوە. لەسەر تەپۆڵکەیەکی بەرزە و بەسەر تەواوی بەشە کۆنەکانی شاردا دەڕوانێت.',
    phone: '',
    hours: '٢٤ کاتژمێر کراوەیە',
    image: 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Citadel',
    isPopular: true,
  },
  {
    id: 'h2',
    name: 'بازاڕی قەیسەری کۆن',
    category: 'historic',
    catName: 'شوێنەوار',
    rating: '4.8',
    address: 'بەرامبەر قەڵای کەرکووک',
    desc: 'بازاڕێکی کەلەپووری مێژوویی سەرپۆشراو بە تاقی بەردین کە مێژووەکەی بۆ سەردەمی عوسمانی دەگەڕێتەوە و ناوەندی فرۆشتنی زێڕ و کەلوپەلی کەلەپوورییە.',
    phone: '',
    hours: '٠٨:٠٠ بەیانی - ٠٨:٠٠ ئێوارە',
    image: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Qaisariya Bazaar Kirkuk',
    isPopular: true,
  },
  {
    id: 'h3',
    name: 'پردی بەردینی خاسە',
    category: 'historic',
    catName: 'شوێنەوار',
    rating: '4.7',
    address: 'سەر ڕووباری خاسە',
    desc: 'پردێکی مێژوویی بەردین کە لە کۆنەوە هەردوو کەناری شار و گەڕەکە دێرینەکانی بەیەکەوە بەستووەتەوە.',
    phone: '',
    hours: 'بەردەوام کراوەیە',
    image: 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Old Stone Bridge Kirkuk',
    isPopular: false,
  },

  // ٢. گەڕەکەکانی کەرکووک
  {
    id: 'n1',
    name: 'گەڕەکی ڕەحیماوا',
    category: 'neighborhoods',
    catName: 'گەڕەک',
    rating: '4.9',
    address: 'باکووری کەرکووک',
    desc: 'گەورەترین و قەرەباڵغترین گەڕەکی شارە. بە بازاڕی شەوانەی چالاک، خواردنە میللییەکان و جۆش و خرۆشی بەردەوامی ناسراوە.',
    phone: '',
    hours: 'ناوچەی نیشتەجێبوون و بازرگانی',
    image: 'https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Rahimawa Kirkuk',
    isPopular: true,
  },
  {
    id: 'n2',
    name: 'گەڕەکی ئەڵماس',
    category: 'neighborhoods',
    catName: 'گەڕەک',
    rating: '4.8',
    address: 'ناوەندی کەرکووک',
    desc: 'گەڕەکێکی مۆدێرن و سەرەکی شار؛ سەنتەری کافێ نوێیەکان، کۆمپانیاکانی ئەلیکترۆنیات، نۆرینگە و دەرمانخانە پزیشکییەکانە.',
    phone: '',
    hours: 'سەنتەری سەرەکی چالاکی شار',
    image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Almas Kirkuk',
    isPopular: true,
  },
  {
    id: 'n3',
    name: 'گەڕەکی ئیسکان',
    category: 'neighborhoods',
    catName: 'گەڕەک',
    rating: '4.7',
    address: 'نزیک ناوەندی شار',
    desc: 'گەڕەکێکی ئارام و خێزانی، نزیک لە زانکۆ و خوێندنگەکان بە شەقامی فراوان و خزمەتگوزاریی تەواوەوە.',
    phone: '',
    hours: 'ناوچەی نیشتەجێبوون',
    image: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Iskan Kirkuk',
    isPopular: false,
  },
  {
    id: 'n4',
    name: 'گەڕەکی شۆرجە',
    category: 'neighborhoods',
    catName: 'گەڕەک',
    rating: '4.8',
    address: 'ناوەندی کەرکووک',
    desc: 'گەڕەکێکی دێرینی شار بە پێگەیەکی مێژوویی تایبەت، بەشێکی گەورەی بازاڕی کەرەستە و ژیانی ڕۆژانەی تێدایە.',
    phone: '',
    hours: 'ناوچەی بازرگانی و نیشتەجێبوون',
    image: 'https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Shorja Kirkuk',
    isPopular: true,
  },

  // ٣. شوێنە خۆشەکان و سەیران
  {
    id: 'f1',
    name: 'پارکی گشتی (باخچەی شار)',
    category: 'fun',
    catName: 'پارک و سەیران',
    rating: '4.6',
    address: 'دڵی سەنتەری کەرکووک',
    desc: 'گەورەترین باخچەی سەوزی شار بۆ پشوودان، پیاسەکردن لەژێر دارە بەتەمەنەکان و شوێنی یاری منداڵان.',
    phone: '',
    hours: '٠٧:٠٠ بەیانی - ١١:٠٠ شەو',
    image: 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Public Park',
    isPopular: true,
  },
  {
    id: 'f2',
    name: 'کۆڕنیشی خاسە',
    category: 'fun',
    catName: 'شوێنی خۆش',
    rating: '4.7',
    address: 'کەنارەکانی ڕووباری خاسە',
    desc: 'شوێنێکی دڵڕفێن بۆ پیاسەی ئێواران بە چەندین کافێی مۆدێرن و بینینی ڕووبار و تیشکی شار.',
    phone: '',
    hours: '٠٤:٠٠ ئێوارە - ١٢:٠٠ شەو',
    image: 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Khasa River Kirkuk',
    isPopular: true,
  },

  // ٥. خواردن و ڕێستۆرانت
  {
    id: 'r1',
    name: 'چێشتخانەی کەبابی خاسە',
    category: 'food',
    catName: 'ڕێستۆرانت',
    rating: '4.9',
    address: 'شەقامی سەرەکی قەڵا',
    desc: 'بەناوبانگترین کەبابی کەرکووک بە گۆشتی خۆماڵی و نانی تەنووری گەرم، تامێکی لەبیرنەکراوی شارەکە.',
    phone: '07701234567',
    hours: '١١:٠٠ نیوەڕۆ - ١١:٠٠ شەو',
    image: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kebab Khasa Kirkuk',
    isPopular: true,
  },
  {
    id: 'r2',
    name: 'کافێ و ڕێستۆرانتی ڤینۆس',
    category: 'food',
    catName: 'کافێ و خواردن',
    rating: '4.7',
    address: 'گەڕەکی ئەڵماس، شەقامی گشتی',
    desc: 'کەشی هاوچەرخ و ئارام بۆ گەنجان و خێزانەکان، پێشکەشکردنی قاوە، شەیک و خواردنە خێرا نێودەوڵەتییەکان.',
    phone: '07707654321',
    hours: '٠٩:٠٠ بەیانی - ١٢:٠٠ شەو',
    image: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Venus Cafe Kirkuk',
    isPopular: false,
  },

  // ٦. بازاڕ و دوکانەکان
  {
    id: 'm1',
    name: 'کەرکووک مۆڵ (Kirkuk Mall)',
    category: 'market',
    catName: 'مۆڵ و بازاڕ',
    rating: '4.8',
    address: 'شەقامی ڕێگای بەغدا',
    desc: 'گەورەترین مۆڵی سەردەمی لە کەرکووک بە فرۆشگای جلوبەرگ، براندە جیهانییەکان، هۆڵی سینەما و بەشی یاری منداڵان.',
    phone: '07709876543',
    hours: '١٠:٠٠ بەیانی - ١١:٣٠ شەو',
    image: 'https://images.unsplash.com/photo-1567449303078-57ad995bd301?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Mall',
    isPopular: true,
  },
  {
    id: 'm2',
    name: 'بازاڕی مۆبایل و تەکنەلۆژیا',
    category: 'market',
    catName: 'ئەلیکترۆنیات',
    rating: '4.6',
    address: 'سەنتەری گەڕەکی ئەڵماس',
    desc: 'سەنتەری سەرەکی بۆ کڕینی مۆبایلە نوێیەکان، چاککردنەوە و ئیکسسواراتی ئەلیکترۆنی لە کەرکووک.',
    phone: '07705554433',
    hours: '٠٩:٠٠ بەیانی - ١٠:٠٠ شەو',
    image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Almas Mobile Market Kirkuk',
    isPopular: false,
  },

  // ٧. خزمەتگوزاری و فریاکەوتن
  {
    id: 's1',
    name: 'نەخۆشخانەی ئازادی فێرکاری',
    category: 'services',
    catName: 'نەخۆشخانە',
    rating: '4.6',
    address: 'گەڕەکی ئازادی',
    desc: 'ناوەندی سەرەکی فریاکەوتنی تەندروستی لە کەرکووک بە پزیشکی پسپۆڕ و بەشەکانی چاودێری چڕ.',
    phone: '122',
    hours: '٢٤ کاتژمێر کراوەیە (فریاکەوتن)',
    image: 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Azadi Hospital Kirkuk',
    isPopular: true,
  },
  {
    id: 's2',
    name: 'پۆلیسی فریاکەوتنی کەرکووک',
    category: 'services',
    catName: 'ئاسایش و فریاکەوتن',
    rating: '4.8',
    address: 'سەنتەری فریاگوزاری شار',
    desc: 'هێڵی گەرم و ڕاستەوخۆی پۆلیسی کەرکووک بۆ پاراستنی هاوڵاتییان لە هەر دۆخێکی بەپەلەدا.',
    phone: '104',
    hours: '٢٤ کاتژمێری شەو و ڕۆژ',
    image: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Police Station',
    isPopular: false,
  },

  // ٨. ڕووداوەکانی کەرکووک
  {
    id: 'e1',
    name: 'فیستیڤاڵی ئاگری نەورۆز لە قەڵا',
    category: 'events',
    catName: 'بۆنەی نەتەوەیی',
    rating: '5.0',
    address: 'سەر تەپۆڵکەی قەڵای کەرکووک',
    desc: 'گەورەترین بۆنەی جەماوەری بە ئامادەبوونی خەڵکی شار بە هەڵکردنی مەشخەڵی ئاگر، مۆسیقای کوردی و جلی ڕازاوە.',
    phone: '',
    hours: '٢٠ی ئادار - کاتژمێر ٠٥:٠٠ ئێوارە',
    image: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Citadel',
    isPopular: true,
  },
  {
    id: 'e2',
    name: 'پێشانگای ساڵانەی کتێب و کلتوور',
    category: 'events',
    catName: 'چالاکی کلتووری',
    rating: '4.7',
    address: 'هۆڵی کلتووری کەرکووک',
    desc: 'کۆکردنەوەی هەزاران کتێبی کوردی و جیهانی لەگەڵ کۆڕی شێعری و ڕێزلێنان لە نووسەرانی شار.',
    phone: '',
    hours: '١٠:٠٠ بەیانی - ٠٦:٠٠ ئێوارە',
    image: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Cultural Center',
    isPopular: false,
  },
];

// لیستەی مێنیوی ٨ بەشە سەرەکییەکە
const SECTIONS = [
  { key: 'home', label: 'سەرەتا', icon: '🏠' },
  { key: 'neighborhoods', label: 'گەڕەکەکان', icon: '🗺️' },
  { key: 'fun', label: 'شوێنی خۆش', icon: '📍' },
  { key: 'historic', label: 'مێژوویی', icon: '🏛️' },
  { key: 'food', label: 'خواردن', icon: '🍽️' },
  { key: 'market', label: 'بازاڕ و دوکان', icon: '🏪' },
  { key: 'services', label: 'خزمەتگوزاری', icon: '🚑' },
  { key: 'events', label: 'ڕووداوەکان', icon: '📅' },
];

export default function App() {
  const [currentTab, setCurrentTab] = useState('home');
  const [search, setSearch] = useState('');
  const [favorites, setFavorites] = useState([]);
  const [isDark, setIsDark] = useState(false);
  const [selectedPlace, setSelectedPlace] = useState(null);

  // دۆخی دڵخوازەکان
  const toggleFavorite = (id) => {
    if (favorites.includes(id)) {
      setFavorites(favorites.filter((fId) => fId !== id));
    } else {
      setFavorites([...favorites, id]);
    }
  };

  // پەیوەندی کردن بە نەخشە
  const openInGoogleMaps = (query) => {
    const url = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query + ' Kirkuk')}`;
    Linking.openURL(url);
  };

  // پەیوەندی تەلەفۆنی ڕاستەوخۆ
  const makePhoneCall = (phoneNumber) => {
    if (phoneNumber) Linking.openURL(`tel:${phoneNumber}`);
  };

  // پاڵاوتنی شوێنەکان بەپێی بەش و گەڕان
  const displayedPlaces = useMemo(() => {
    let list = ALL_PLACES;

    if (currentTab === 'home') {
      if (!search.trim()) {
        return list; // لە پەڕەی سەرەتا هەمووی پیشان دەدات
      }
    } else {
      list = list.filter((item) => item.category === currentTab);
    }

    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(
        (item) =>
          item.name.toLowerCase().includes(q) ||
          item.desc.toLowerCase().includes(q) ||
          item.address.toLowerCase().includes(q) ||
          item.catName.toLowerCase().includes(q)
      );
    }
    return list;
  }, [currentTab, search]);

  // شوێنە پڕبینراوەکانی سەرەتا
  const popularPlaces = useMemo(() => ALL_PLACES.filter((p) => p.isPopular), []);

  // ڕەنگەکانی دۆخی ڕووناک و تاریک
  const theme = {
    bg: isDark ? '#090d16' : '#f8fafc',
    card: isDark ? '#131b2e' : '#ffffff',
    text: isDark ? '#f1f5f9' : '#0f172a',
    subText: isDark ? '#94a3b8' : '#64748b',
    border: isDark ? '#1e293b' : '#e2e8f0',
    primary: '#0284c7',
    accent: '#f59e0b',
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.bg }]}>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} />

      {/* بەشی سەرەوەی ئەپڵیکەیشن (Header) */}
      <View style={[styles.header, { backgroundColor: theme.card, borderBottomColor: theme.border }]}>
        <View style={styles.headerTop}>
          <TouchableOpacity
            onPress={() => setIsDark(!isDark)}
            style={[styles.themeBtn, { backgroundColor: isDark ? '#1e293b' : '#f1f5f9' }]}
          >
            <Text style={{ fontSize: 18 }}>{isDark ? '☀️' : '🌙'}</Text>
          </TouchableOpacity>

          <View style={{ alignItems: 'flex-end' }}>
            <Text style={[styles.appTitle, { color: theme.text }]}>ڕێبەری کەرکووک</Text>
            <Text style={[styles.appSub, { color: theme.subText }]}>دەروازەی تەواوی گەڕەک و شوێنەکان</Text>
          </View>
        </View>

        {/* گەڕانی زیرەک */}
        <View style={[styles.searchBox, { backgroundColor: theme.bg, borderColor: theme.border }]}>
          <TextInput
            style={[styles.searchInput, { color: theme.text }]}
            placeholder="گەڕان بۆ گەڕەک، چێشتخانە، نەخۆشخانە..."
            placeholderTextColor={theme.subText}
            value={search}
            onChangeText={setSearch}
          />
          <Text style={{ fontSize: 16 }}>🔍</Text>
        </View>

        {/* لیستی ٨ بەشە سەرەکییەکە */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabsScroll}>
          {SECTIONS.map((sec) => {
            const isActive = currentTab === sec.key;
            return (
              <TouchableOpacity
                key={sec.key}
                onPress={() => setCurrentTab(sec.key)}
                style={[
                  styles.tabChip,
                  isActive
                    ? { backgroundColor: theme.primary, borderColor: theme.primary }
                    : { backgroundColor: theme.bg, borderColor: theme.border },
                ]}
              >
                <Text style={[styles.tabLabel, isActive ? { color: '#ffffff' } : { color: theme.subText }]}>
                  {sec.icon} {sec.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* ناوەڕۆکی لاپەڕەکە */}
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 60 }}>
        {/* ئەگەر لە بەشی سەرەتا بێت و گەڕان نەکرابێت: هێرۆ و شوێنە پڕبینراوەکان پیشان بدە */}
        {currentTab === 'home' && !search && (
          <View>
            {/* وێنەی کەشخەی کەرکووک */}
            <View style={styles.heroBox}>
              <Image
                source={{ uri: 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1000&q=80' }}
                style={styles.heroImg}
              />
              <View style={styles.heroOverlay}>
                <Text style={styles.heroTag}>🌟 شاری کەرکووک</Text>
                <Text style={styles.heroTitle}>بەخێربێن بۆ دڵی شار</Text>
                <Text style={styles.heroDesc}>گەشتی خۆت بەناو کەلەپوور، بازاڕ و خۆشترین شوێنەکان دەستپێبکە.</Text>
              </View>
            </View>

            {/* شوێنە پڕبینراوەکان (Popular) */}
            <View style={styles.sectionHeader}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>🔥 شوێنە پڕبینراوەکان</Text>
              <Text style={[styles.sectionSubtitle, { color: theme.subText }]}>هەڵبژاردەی هاوڵاتییان و گەشتیاران</Text>
            </View>

            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ paddingHorizontal: 16 }}>
              {popularPlaces.map((pop) => (
                <TouchableOpacity
                  key={pop.id}
                  style={[styles.popCard, { backgroundColor: theme.card, borderColor: theme.border }]}
                  onPress={() => setSelectedPlace(pop)}
                >
                  <Image source={{ uri: pop.image }} style={styles.popImg} />
                  <View style={{ padding: 10 }}>
                    <Text style={[styles.popTitle, { color: theme.text }]} numberOfLines={1}>
                      {pop.name}
                    </Text>
                    <Text style={[styles.popCat, { color: theme.primary }]}>{pop.catName}</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <View style={[styles.sectionHeader, { marginTop: 24 }]}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>📌 هەموو شوێنەکان</Text>
              <Text style={[styles.sectionSubtitle, { color: theme.subText }]}>گەڕان بەناو لیستی تەواودا</Text>
            </View>
          </View>
        )}

        {/* کاردە سەرەکییەکانی هەر شوێنێک */}
        <View style={{ paddingHorizontal: 16 }}>
          {displayedPlaces.length === 0 ? (
            <View style={styles.emptyBox}>
              <Text style={{ fontSize: 40, marginBottom: 10 }}>🔍</Text>
              <Text style={[styles.emptyText, { color: theme.text }]}>هیچ شوێنێک نەدۆزرایەوە!</Text>
              <Text style={[styles.emptySub, { color: theme.subText }]}>وشەیەکی تر بنووسە یان بەشێکی تر هەڵبژێرە.</Text>
            </View>
          ) : (
            displayedPlaces.map((item) => {
              const isFav = favorites.includes(item.id);
              return (
                <View
                  key={item.id}
                  style={[styles.card, { backgroundColor: theme.card, borderColor: theme.border }]}
                >
                  {/* وێنەی کاردەکە و ڕەیتینگ */}
                  <View style={styles.cardImgWrapper}>
                    <Image source={{ uri: item.image }} style={styles.cardImg} />
                    <TouchableOpacity
                      style={styles.favBadge}
                      onPress={() => toggleFavorite(item.id)}
                    >
                      <Text style={{ fontSize: 16 }}>{isFav ? '❤️' : '🤍'}</Text>
                    </TouchableOpacity>
                    <View style={styles.rateBadge}>
                      <Text style={styles.rateText}>⭐ {item.rating}</Text>
                    </View>
                    <View style={styles.categoryBadge}>
                      <Text style={styles.categoryBadgeText}>{item.catName}</Text>
                    </View>
                  </View>

                  {/* زانیارییەکانی شوێنەکە */}
                  <View style={styles.cardDetails}>
                    <Text style={[styles.cardTitle, { color: theme.text }]}>{item.name}</Text>
                    <Text style={[styles.cardLoc, { color: theme.primary }]}>📍 {item.address}</Text>
                    <Text style={[styles.cardDesc, { color: theme.subText }]} numberOfLines={2}>
                      {item.desc}
                    </Text>

                    {item.hours ? (
                      <Text style={[styles.cardHours, { color: theme.subText }]}>🕒 {item.hours}</Text>
                    ) : null}

                    {/* دوگمەکانی نەخشە و پەیوەندی */}
                    <View style={[styles.cardActions, { borderTopColor: theme.border }]}>
                      <TouchableOpacity
                        style={[styles.btnMap, { backgroundColor: theme.primary }]}
                        onPress={() => openInGoogleMaps(item.mapQuery)}
                      >
                        <Text style={styles.btnTextWhite}>🗺️ کردنەوە لە نەخشە</Text>
                      </TouchableOpacity>

                      {item.phone ? (
                        <TouchableOpacity
                          style={styles.btnCall}
                          onPress={() => makePhoneCall(item.phone)}
                        >
                          <Text style={styles.btnTextWhite}>📞 {item.phone}</Text>
                        </TouchableOpacity>
                      ) : null}

                      <TouchableOpacity
                        style={[styles.btnDetails, { backgroundColor: theme.bg, borderColor: theme.border }]}
                        onPress={() => setSelectedPlace(item)}
                      >
                        <Text style={[styles.btnTextDetail, { color: theme.text }]}>📖 زانیاری</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                </View>
              );
            })
          )}
        </View>
      </ScrollView>

      {/* مۆداڵی وردەکاریی تەواوی شوێنەکە (Card Detail View) */}
      {selectedPlace && (
        <Modal animationType="slide" transparent={true} visible={true} onRequestClose={() => setSelectedPlace(null)}>
          <View style={styles.modalOverlay}>
            <View style={[styles.modalBox, { backgroundColor: theme.card }]}>
              <Image source={{ uri: selectedPlace.image }} style={styles.modalImg} />
              <TouchableOpacity style={styles.closeModalBtn} onPress={() => setSelectedPlace(null)}>
                <Text style={{ fontSize: 18, color: '#fff', fontWeight: 'bold' }}>✕</Text>
              </TouchableOpacity>

              <ScrollView style={{ padding: 18 }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text style={[styles.modalTitle, { color: theme.text }]}>{selectedPlace.name}</Text>
                  <Text style={{ fontSize: 16, color: '#f59e0b', fontWeight: 'bold' }}>⭐ {selectedPlace.rating}</Text>
                </View>

                <Text style={{ color: theme.primary, fontWeight: 'bold', marginVertical: 6 }}>
                  📍 {selectedPlace.address}
                </Text>

                {selectedPlace.hours ? (
                  <Text style={{ color: theme.subText, fontSize: 13, marginBottom: 12 }}>
                    🕒 کاتژمێر: {selectedPlace.hours}
                  </Text>
                ) : null}

                <Text style={[styles.modalDescTitle, { color: theme.text }]}>دەربارەی ئەم شوێنە:</Text>
                <Text style={[styles.modalDesc, { color: theme.subText }]}>{selectedPlace.desc}</Text>

                <View style={{ marginTop: 24, gap: 10 }}>
                  <TouchableOpacity
                    style={[styles.btnMap, { backgroundColor: theme.primary, paddingVertical: 14 }]}
                    onPress={() => openInGoogleMaps(selectedPlace.mapQuery)}
                  >
                    <Text style={styles.btnTextWhite}>🗺️ شوێن لەسەر گووگڵ ماپس (Google Maps)</Text>
                  </TouchableOpacity>

                  {selectedPlace.phone ? (
                    <TouchableOpacity
                      style={[styles.btnCall, { paddingVertical: 14 }]}
                      onPress={() => makePhoneCall(selectedPlace.phone)}
                    >
                      <Text style={styles.btnTextWhite}>📞 پەیوەندیکردن: {selectedPlace.phone}</Text>
                    </TouchableOpacity>
                  ) : null}
                </View>
              </ScrollView>
            </View>
          </View>
        </Modal>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { padding: 16, borderBottomWidth: 1 },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  appTitle: { fontSize: 24, fontWeight: '900', letterSpacing: 0.5 },
  appSub: { fontSize: 12, marginTop: 2 },
  themeBtn: { width: 42, height: 42, borderRadius: 21, alignItems: 'center', justifyContent: 'center' },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 25,
    borderWidth: 1,
    paddingHorizontal: 16,
    height: 46,
    marginBottom: 12,
  },
  searchInput: { flex: 1, textAlign: 'right', fontSize: 13, paddingRight: 8 },
  tabsScroll: { marginTop: 4 },
  tabChip: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 20,
    borderWidth: 1,
    marginRight: 8,
  },
  tabLabel: { fontSize: 12, fontWeight: '700' },
  heroBox: {
    margin: 16,
    height: 190,
    borderRadius: 24,
    overflow: 'hidden',
    position: 'relative',
  },
  heroImg: { width: '100%', height: '100%' },
  heroOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.48)',
    justifyContent: 'flex-end',
    padding: 16,
  },
  heroTag: { color: '#fbbf24', fontSize: 12, fontWeight: 'bold', marginBottom: 4 },
  heroTitle: { color: '#ffffff', fontSize: 22, fontWeight: 'bold' },
  heroDesc: { color: '#e2e8f0', fontSize: 12, marginTop: 4 },
  sectionHeader: { paddingHorizontal: 16, marginBottom: 12 },
  sectionTitle: { fontSize: 18, fontWeight: '800' },
  sectionSubtitle: { fontSize: 12, marginTop: 2 },
  popCard: {
    width: 140,
    borderRadius: 16,
    borderWidth: 1,
    overflow: 'hidden',
    marginRight: 12,
    marginBottom: 8,
  },
  popImg: { width: '100%', height: 95 },
  popTitle: { fontSize: 13, fontWeight: 'bold', textAlign: 'right' },
  popCat: { fontSize: 11, textAlign: 'right', marginTop: 2, fontWeight: '600' },
  card: {
    borderRadius: 22,
    borderWidth: 1,
    marginBottom: 18,
    overflow: 'hidden',
    elevation: 3,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 10,
  },
  cardImgWrapper: { height: 190, width: '100%', position: 'relative' },
  cardImg: { width: '100%', height: '100%' },
  favBadge: {
    position: 'absolute',
    top: 12,
    left: 12,
    backgroundColor: 'rgba(255,255,255,0.92)',
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rateBadge: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    backgroundColor: 'rgba(15,23,42,0.75)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  rateText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  categoryBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: 'rgba(2,132,199,0.9)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  categoryBadgeText: { color: '#fff', fontSize: 11, fontWeight: 'bold' },
  cardDetails: { padding: 16 },
  cardTitle: { fontSize: 18, fontWeight: '800', textAlign: 'right', marginBottom: 4 },
  cardLoc: { fontSize: 12, textAlign: 'right', fontWeight: 'bold', marginBottom: 6 },
  cardDesc: { fontSize: 13, lineHeight: 20, textAlign: 'right', marginBottom: 8 },
  cardHours: { fontSize: 11, textAlign: 'right', marginBottom: 12 },
  cardActions: {
    flexDirection: 'row',
    paddingTop: 12,
    borderTopWidth: 1,
    gap: 8,
    alignItems: 'center',
  },
  btnMap: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: 'center',
  },
  btnCall: {
    backgroundColor: '#10b981',
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  btnDetails: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
  },
  btnTextWhite: { color: '#ffffff', fontSize: 12, fontWeight: 'bold' },
  btnTextDetail: { fontSize: 12, fontWeight: 'bold' },
  emptyBox: { alignItems: 'center', justifyContent: 'center', paddingVertical: 50 },
  emptyText: { fontSize: 16, fontWeight: 'bold' },
  emptySub: { fontSize: 12, marginTop: 4 },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'flex-end',
  },
  modalBox: {
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    maxHeight: '85%',
    overflow: 'hidden',
  },
  modalImg: { width: '100%', height: 220 },
  closeModalBtn: {
    position: 'absolute',
    top: 16,
    left: 16,
    backgroundColor: 'rgba(0,0,0,0.6)',
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalTitle: { fontSize: 20, fontWeight: '900', textAlign: 'right' },
  modalDescTitle: { fontSize: 14, fontWeight: 'bold', textAlign: 'right', marginTop: 14, marginBottom: 4 },
  modalDesc: { fontSize: 13, lineHeight: 22, textAlign: 'right' },
});

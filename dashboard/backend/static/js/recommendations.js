// recommendations.js - Script pour la page de recommandations de fournisseurs durables

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation de la page
    initPage();

    // Gestionnaires d'événements pour les filtres
    document.getElementById('minScore').addEventListener('input', updateSliderValue);
    document.getElementById('minRenewable').addEventListener('input', updateSliderValue);
    document.getElementById('applyFilters').addEventListener('click', applyFilters);

    // Gestionnaire pour le bouton d'analyse IA
    document.getElementById('analysisBtn').addEventListener('click', showAIAnalysis);

    // Gestionnaire pour fermer la modale
    document.querySelector('.close').addEventListener('click', closeModal);
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('aiAnalysisModal');
        if (event.target == modal) {
            closeModal();
        }
    });
});

// Initialisation de la page
function initPage() {
    console.log("Initialisation de la page de recommandations");
    
    // Vérifier si les éléments nécessaires existent pour éviter les erreurs
    if (!document.getElementById('suppliersLoading') || !document.getElementById('suppliersGrid')) {
        console.error("Éléments DOM requis non trouvés. Vérifiez la structure HTML.");
        return;
    }
    
    // Utiliser un délai court pour s'assurer que DOM est complètement chargé
    setTimeout(() => {
        // Charger les données des fournisseurs
        fetchSupplierRecommendations();
    }, 100);
    
    // Ajout d'un gestionnaire pour les erreurs de graphiques
    Chart.defaults.plugins.title.display = true;
    Chart.defaults.plugins.title.font = {
        size: 16,
        weight: 'bold'
    };
}

// Mise à jour des valeurs affichées des sliders
function updateSliderValue(e) {
    const value = e.target.value;
    document.getElementById(`${e.target.id}Value`).textContent = value;
}

// Récupération des recommandations de fournisseurs
function fetchSupplierRecommendations(filters = {}) {
    // Afficher l'indicateur de chargement
    document.getElementById('suppliersLoading').style.display = 'flex';
    document.getElementById('suppliersGrid').innerHTML = '';
    
    // Construire l'URL avec les paramètres de requête
    let url = '/api/recommendations?count=10';
    
    // Pour déboguer - montrer la requête dans la console
    console.log("Envoi de la requête à:", url);
    
    // Effectuer la requête AJAX
    fetch(url)
        .then(response => {
            console.log("Statut de la réponse:", response.status);
            if (!response.ok) {
                throw new Error(`Erreur lors de la récupération des recommandations: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Données reçues:", data);
            
            // Vérifier la structure des données
            if (!data || !data.recommendations || !Array.isArray(data.recommendations)) {
                throw new Error("Format de données invalide");
            }
            
            // Masquer l'indicateur de chargement
            document.getElementById('suppliersLoading').style.display = 'none';
            
            // Filtrer les données si nécessaire
            let filteredData = filterData(data.recommendations, filters);
            
            // Afficher les données
            displaySuppliers(filteredData);
            
            // Créer les visualisations si les données de visualisation sont disponibles
            if (data.visualization_data) {
                createCharts(data.visualization_data, filteredData);
            } else {
                console.warn("Données de visualisation non disponibles");
                // Créer les visualisations avec les données filtrées directement
                createChartsFromSuppliers(filteredData);
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            document.getElementById('suppliersLoading').style.display = 'none';
            document.getElementById('suppliersGrid').innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Impossible de charger les recommandations. Veuillez réessayer plus tard.</p>
                    <p class="error-details">Détail: ${error.message}</p>
                </div>
            `;
        });
}

// Filtrer les données selon les critères sélectionnés
function filterData(data, filters) {
    if (Object.keys(filters).length === 0) return data;
    
    return data.filter(supplier => {
        let passFilter = true;
        
        // Filtre par score minimum
        if (filters.minScore && supplier.sustainability_score < filters.minScore) {
            passFilter = false;
        }
        
        // Filtre par pourcentage minimum d'énergie renouvelable
        if (filters.minRenewable && supplier.renewable_energy_percentage < filters.minRenewable) {
            passFilter = false;
        }
        
        // Filtre par type de transport
        if (filters.transport && filters.transport !== 'all') {
            const transportMapping = {
                'electric': 'Électrique',
                'hybrid': 'Hybride',
                'rail': 'Ferroviaire',
                'ship': 'Maritime',
                'truck': 'Camionnage',
                'air': 'Aérien'
            };
            
            if (supplier.transport_type !== transportMapping[filters.transport]) {
                passFilter = false;
            }
        }
        
        return passFilter;
    });
}

// Afficher les fournisseurs dans la grille
function displaySuppliers(suppliers) {
    const grid = document.getElementById('suppliersGrid');
    if (!grid) {
        console.error("Élément DOM 'suppliersGrid' non trouvé");
        return;
    }
    
    grid.innerHTML = '';
    
    if (!suppliers || suppliers.length === 0) {
        grid.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <p>Aucun fournisseur ne correspond à vos critères. Veuillez modifier vos filtres.</p>
            </div>
        `;
        return;
    }
    
    // Enregistrer les erreurs potentielles sans interrompre l'affichage
    let errorCount = 0;
    
    suppliers.forEach((supplier, index) => {
        try {
            // Vérifier les propriétés essentielles
            if (!supplier.supplier_name) {
                console.warn(`Fournisseur à l'index ${index} sans nom, utilisation d'un nom par défaut`);
                supplier.supplier_name = `Fournisseur #${index + 1}`;
            }
            
            if (typeof supplier.sustainability_score !== 'number') {
                console.warn(`Score de durabilité invalide pour ${supplier.supplier_name}, utilisation d'une valeur par défaut`);
                supplier.sustainability_score = 0;
            }
            
            // Créer la carte du fournisseur avec gestion des valeurs manquantes
            const card = document.createElement('div');
            card.className = 'supplier-card';
            
            // Déterminer la classe de score (couleur)
            let scoreClass = 'low';
            if (supplier.sustainability_score >= 75) {
                scoreClass = 'high';
            } else if (supplier.sustainability_score >= 50) {
                scoreClass = 'medium';
            }
            
            // Formater les certifications avec gestion des valeurs nulles
            let certifications = '<span class="certification-badge empty">Aucune certification</span>';
            if (supplier.environmental_certifications && typeof supplier.environmental_certifications === 'string') {
                const certList = supplier.environmental_certifications.split(',').filter(cert => cert.trim());
                if (certList.length > 0) {
                    certifications = certList.map(cert => `<span class="certification-badge">${cert.trim()}</span>`).join('');
                }
            }
            
            // Assurer que les valeurs numériques existent et sont des nombres
            const renewableEnergy = typeof supplier.renewable_energy_percentage === 'number' ? 
                supplier.renewable_energy_percentage : 0;
            
            const carbonFootprint = typeof supplier.avg_carbon_footprint === 'number' ? 
                supplier.avg_carbon_footprint.toFixed(2) : 'N/A';
            
            const waterConsumption = typeof supplier.avg_water_consumption === 'number' ? 
                supplier.avg_water_consumption.toFixed(2) : 'N/A';
            
            card.innerHTML = `
                <div class="supplier-header">
                    <h3>${supplier.supplier_name}</h3>
                    <div class="score-badge ${scoreClass}">${supplier.sustainability_score.toFixed(1)}</div>
                </div>
                <div class="supplier-location">
                    <i class="fas fa-map-marker-alt"></i> ${supplier.location || 'Non spécifié'}
                </div>
                <div class="supplier-metrics">
                    <div class="metric">
                        <i class="fas fa-leaf"></i>
                        <span>Énergie renouvelable:</span>
                        <strong>${renewableEnergy}%</strong>
                    </div>
                    <div class="metric">
                        <i class="fas fa-cloud"></i>
                        <span>Empreinte carbone:</span>
                        <strong>${carbonFootprint} kgCO₂e</strong>
                    </div>
                    <div class="metric">
                        <i class="fas fa-tint"></i>
                        <span>Consommation d'eau:</span>
                        <strong>${waterConsumption} L</strong>
                    </div>
                    <div class="metric">
                        <i class="fas fa-truck"></i>
                        <span>Transport:</span>
                        <strong>${supplier.transport_type || 'Non spécifié'}</strong>
                    </div>
                </div>
                <div class="supplier-certifications">
                    <h4>Certifications:</h4>
                    <div class="certifications-container">
                        ${certifications}
                    </div>
                </div>
                <a href="/details/${supplier.supplier_id}" class="btn secondary-btn">Voir détails</a>
            `;
            
            grid.appendChild(card);
        } catch (error) {
            console.error(`Erreur lors de l'affichage du fournisseur ${index}:`, error);
            errorCount++;
            
            // Si ce n'est que le premier fournisseur qui pose problème, essayons d'afficher un message
            if (errorCount === 1 && index === 0) {
                // Créer une carte d'erreur plus informative
                const errorCard = document.createElement('div');
                errorCard.className = 'supplier-card error-card';
                errorCard.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erreur d'affichage pour certains fournisseurs</p>
                        <details>
                            <summary>Détails techniques</summary>
                            <code>${error.message}</code>
                        </details>
                    </div>
                `;
                grid.appendChild(errorCard);
            }
        }
    });
    
    // Si tous les fournisseurs ont généré des erreurs, afficher un message global
    if (errorCount === suppliers.length) {
        grid.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Impossible d'afficher les fournisseurs en raison d'erreurs de format de données.</p>
                <p>Veuillez contacter l'administrateur système.</p>
            </div>
        `;
    }
}

// Créer les graphiques à partir des données de visualisation
function createCharts(visualizationData, filteredData) {
    try {
        // Utiliser les données filtrées pour les graphiques
        const supplierNames = filteredData.map(supplier => supplier.supplier_name);
        const sustainabilityScores = filteredData.map(supplier => supplier.sustainability_score);
        
        // 1. Graphique des scores de durabilité
        createSustainabilityChart(supplierNames, sustainabilityScores);
        
        // 2. Graphique de répartition par type de transport
        createTransportChart(filteredData);
        
        // 3. Graphique Énergie renouvelable vs Empreinte carbone
        createEnergyVsCarbonChart(filteredData);
    } catch (error) {
        console.error("Erreur lors de la création des graphiques:", error);
        // Afficher un message d'erreur sur les conteneurs de graphiques
        displayChartError();
    }
}

// Créer les graphiques directement à partir des données des fournisseurs
function createChartsFromSuppliers(suppliers) {
    try {
        if (!suppliers || suppliers.length === 0) {
            throw new Error("Aucune donnée de fournisseur disponible pour les graphiques");
        }
        
        const supplierNames = suppliers.map(supplier => supplier.supplier_name);
        const sustainabilityScores = suppliers.map(supplier => supplier.sustainability_score);
        
        // 1. Graphique des scores de durabilité
        createSustainabilityChart(supplierNames, sustainabilityScores);
        
        // 2. Graphique de répartition par type de transport
        createTransportChart(suppliers);
        
        // 3. Graphique Énergie renouvelable vs Empreinte carbone
        createEnergyVsCarbonChart(suppliers);
    } catch (error) {
        console.error("Erreur lors de la création des graphiques:", error);
        // Afficher un message d'erreur sur les conteneurs de graphiques
        displayChartError();
    }
}

// Afficher un message d'erreur dans les conteneurs de graphiques
function displayChartError() {
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        const canvas = container.querySelector('canvas');
        if (canvas) {
            // Masquer le canvas
            canvas.style.display = 'none';
            
            // Créer un message d'erreur
            const errorDiv = document.createElement('div');
            errorDiv.className = 'chart-error';
            errorDiv.innerHTML = `
                <i class="fas fa-chart-bar"></i>
                <p>Impossible de charger le graphique</p>
            `;
            
            // Ajouter le message après le titre
            const title = container.querySelector('h3');
            if (title) {
                title.insertAdjacentElement('afterend', errorDiv);
            } else {
                container.appendChild(errorDiv);
            }
        }
    });
}

// Graphique des scores de durabilité
function createSustainabilityChart(labels, scores) {
    const ctx = document.getElementById('sustainabilityChart').getContext('2d');
    
    // Détruire le graphique précédent s'il existe
    if (window.sustainabilityChart) {
        window.sustainabilityChart.destroy();
    }
    
    window.sustainabilityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score de durabilité',
                data: scores,
                backgroundColor: scores.map(score => {
                    if (score >= 75) return 'rgba(46, 204, 113, 0.7)';
                    if (score >= 50) return 'rgba(241, 196, 15, 0.7)';
                    return 'rgba(231, 76, 60, 0.7)';
                }),
                borderColor: scores.map(score => {
                    if (score >= 75) return 'rgb(39, 174, 96)';
                    if (score >= 50) return 'rgb(243, 156, 18)';
                    return 'rgb(192, 57, 43)';
                }),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Score de durabilité (/100)'
                    }
                },
                x: {
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Score: ${context.raw.toFixed(1)}/100`;
                        }
                    }
                }
            }
        }
    });
}

// Graphique de répartition par type de transport
function createTransportChart(suppliers) {
    const ctx = document.getElementById('transportChart').getContext('2d');
    
    // Compter les types de transport
    const transportTypes = {};
    suppliers.forEach(supplier => {
        const type = supplier.transport_type || 'Non spécifié';
        transportTypes[type] = (transportTypes[type] || 0) + 1;
    });
    
    // Préparer les données pour le graphique
    const labels = Object.keys(transportTypes);
    const data = Object.values(transportTypes);
    
    // Couleurs pour les différents types de transport
    const colors = {
        'Électrique': 'rgba(46, 204, 113, 0.7)',
        'Hybride': 'rgba(241, 196, 15, 0.7)',
        'Ferroviaire': 'rgba(52, 152, 219, 0.7)',
        'Maritime': 'rgba(155, 89, 182, 0.7)',
        'Camionnage': 'rgba(230, 126, 34, 0.7)',
        'Aérien': 'rgba(231, 76, 60, 0.7)',
        'Multimodal': 'rgba(52, 73, 94, 0.7)',
        'Non spécifié': 'rgba(189, 195, 199, 0.7)'
    };
    
    // Détruire le graphique précédent s'il existe
    if (window.transportChart) {
        window.transportChart.destroy();
    }
    
    window.transportChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: labels.map(label => colors[label] || 'rgba(189, 195, 199, 0.7)'),
                borderColor: 'white',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Graphique Énergie renouvelable vs Empreinte carbone
function createEnergyVsCarbonChart(suppliers) {
    const ctx = document.getElementById('energyVsCarbonChart').getContext('2d');
    
    // Préparer les données pour le graphique
    const data = suppliers.map(supplier => ({
        x: supplier.renewable_energy_percentage,
        y: supplier.avg_carbon_footprint,
        r: calculateBubbleSize(supplier.sustainability_score),
        name: supplier.supplier_name,
        score: supplier.sustainability_score
    }));
    
    // Détruire le graphique précédent s'il existe
    if (window.energyVsCarbonChart) {
        window.energyVsCarbonChart.destroy();
    }
    
    window.energyVsCarbonChart = new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Fournisseurs',
                data: data,
                backgroundColor: data.map(item => {
                    // Couleur basée sur le score de durabilité
                    if (item.score >= 75) return 'rgba(46, 204, 113, 0.7)';
                    if (item.score >= 50) return 'rgba(241, 196, 15, 0.7)';
                    return 'rgba(231, 76, 60, 0.7)';
                }),
                borderColor: 'rgba(52, 73, 94, 0.5)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Énergie renouvelable (%)'
                    },
                    min: 0,
                    max: 100
                },
                y: {
                    title: {
                        display: true,
                        text: 'Empreinte carbone (kgCO₂e)'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = context.raw;
                            return [
                                `${item.name}`,
                                `Score: ${item.score.toFixed(1)}/100`,
                                `Énergie renouvelable: ${item.x}%`,
                                `Empreinte carbone: ${item.y.toFixed(2)} kgCO₂e`
                            ];
                        }
                    }
                }
            }
        }
    });
}

// Calculer la taille des bulles pour le graphique
function calculateBubbleSize(score) {
    // Taille de bulle entre 5 et 20 basée sur le score
    return 5 + (score / 100) * 15;
}

// Appliquer les filtres
function applyFilters() {
    const minScore = parseInt(document.getElementById('minScore').value);
    const minRenewable = parseInt(document.getElementById('minRenewable').value);
    const transport = document.getElementById('transport').value;
    
    const filters = {
        minScore: minScore,
        minRenewable: minRenewable,
        transport: transport
    };
    
    fetchSupplierRecommendations(filters);
}

// Afficher la modale d'analyse IA
function showAIAnalysis() {
    const modal = document.getElementById('aiAnalysisModal');
    modal.style.display = 'flex';
    document.getElementById('analysisLoader').style.display = 'flex';
    document.getElementById('analysisContent').innerHTML = '';
    
    // Récupérer l'analyse IA
    fetch('/api/llm_analysis')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération de l\'analyse IA');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('analysisLoader').style.display = 'none';
            
            // Convertir le contenu Markdown en HTML
            const analysisHtml = marked.parse(data.analysis);
            
            document.getElementById('analysisContent').innerHTML = `
                <div class="analysis-text">
                    ${analysisHtml}
                </div>
                <div class="top-suppliers">
                    <h3>Top 3 fournisseurs recommandés</h3>
                    <div class="top-suppliers-grid">
                        ${data.top_suppliers.map((supplier, index) => createTopSupplierCard(supplier, index)).join('')}
                    </div>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erreur:', error);
            document.getElementById('analysisLoader').style.display = 'none';
            document.getElementById('analysisContent').innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Impossible de charger l'analyse IA. Veuillez réessayer plus tard.</p>
                </div>
            `;
        });
}

// Créer une carte pour les top fournisseurs dans l'analyse IA
function createTopSupplierCard(supplier, index) {
    const medals = ['🥇', '🥈', '🥉'];
    const medal = index < medals.length ? medals[index] : '';
    
    return `
        <div class="top-supplier-card">
            <div class="top-supplier-header">
                <span class="medal">${medal}</span>
                <h4>${supplier.supplier_name}</h4>
                <div class="score-badge ${getScoreClass(supplier.sustainability_score)}">
                    ${supplier.sustainability_score.toFixed(1)}
                </div>
            </div>
            <div class="top-supplier-metrics">
                <div class="metric">
                    <i class="fas fa-leaf"></i>
                    <span>Énergie renouvelable:</span>
                    <strong>${supplier.renewable_energy_percentage}%</strong>
                </div>
                <div class="metric">
                    <i class="fas fa-cloud"></i>
                    <span>Empreinte carbone:</span>
                    <strong>${supplier.avg_carbon_footprint.toFixed(2)} kgCO₂e</strong>
                </div>
            </div>
        </div>
    `;
}

// Obtenir la classe CSS pour un score donné
function getScoreClass(score) {
    if (score >= 75) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
}

// Fermer la modale
function closeModal() {
    document.getElementById('aiAnalysisModal').style.display = 'none';
}
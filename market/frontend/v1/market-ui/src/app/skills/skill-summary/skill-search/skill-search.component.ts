import { Component, EventEmitter, OnInit, OnDestroy, Output } from '@angular/core';

import { Subscription } from "rxjs/internal/Subscription";
import { faArrowLeft, faSearch } from '@fortawesome/free-solid-svg-icons';

import { SkillsService } from "../../skills.service";

@Component({
    selector: 'market-skill-search',
    templateUrl: './skill-search.component.html',
    styleUrls: ['./skill-search.component.scss']
})
export class SkillSearchComponent implements OnInit, OnDestroy {
    public backArrow = faArrowLeft;
    public searchIcon = faSearch;
    @Output() public searchResults = new EventEmitter();
    public searchTerm: string;
    public skillsAreFiltered: Subscription;
    public showBackButton: boolean = false;

    constructor(private skillsService: SkillsService) { }

    ngOnInit() {
        this.skillsAreFiltered = this.skillsService.isFiltered.subscribe(
            (isFiltered) => { this.onFilteredStateChange(isFiltered) }
        );
    }

    ngOnDestroy() {
        this.skillsAreFiltered.unsubscribe();
    }

    /** Clear out the contents of the search bar. */
    clearSearch(): void {
        this.searchTerm = '';
        this.searchSkills()
    }

    /** Call the skill search API to return skills matching the search criteria. */
    searchSkills(): void {
        this.skillsService.searchSkills(this.searchTerm).subscribe(
            (skills) => {
                this.searchResults.emit(skills);
            }
        );
    }

    /** Determine whether or not to show the back button. */
    onFilteredStateChange (isFiltered) {
        this.showBackButton = isFiltered
    }
}
